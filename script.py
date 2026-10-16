from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parent
DEMUCS_MODEL = "htdemucs_ft"
DRUMSEP_MODEL = "MDX23C-DrumSep-aufr33-jarredou.ckpt"
DRUMSEP_MODEL_CACHE = Path.home() / ".cache" / "ailoop" / "models"

DEMUCS_STEMS = ("drums", "bass", "other", "vocals")
DRUM_PARTS = {
    "kick": ("kick",),
    "snare": ("snare",),
    "toms": ("toms",),
    "hihat": ("hihat", "hi-hat", "hh"),
    "ride": ("ride",),
    "crash": ("crash",),
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Separate a mix into Demucs stems and six drum-kit stems."
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input audio file (.wav or .mp3).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output WAV files with the same input prefix.",
    )
    return parser.parse_args(argv)


def validate_input(input_path: Path) -> Path:
    input_path = input_path.expanduser().resolve()
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if input_path.suffix.lower() not in {".wav", ".mp3"}:
        raise ValueError("Input must be a WAV or MP3 file.")
    return input_path


def _find_demucs_outputs(work_dir: Path, track_name: str) -> dict[str, Path]:
    track_dir = work_dir / DEMUCS_MODEL / track_name
    stems = {stem: track_dir / f"{stem}.wav" for stem in DEMUCS_STEMS}
    missing = [str(path) for path in stems.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Demucs did not produce expected stem files: {', '.join(missing)}")
    return stems


def _resolve_separator_outputs(output_dir: Path, filenames: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for filename in filenames:
        path = Path(filename)
        if not path.is_absolute():
            path = output_dir / path
        if not path.is_file():
            raise RuntimeError(f"Drum separator reported a missing output file: {path}")
        paths.append(path)
    return paths


def _part_for_filename(filename: str) -> str | None:
    name = Path(filename).stem.lower()
    for part, aliases in DRUM_PARTS.items():
        for alias in aliases:
            if re.search(rf"(?<![a-z]){re.escape(alias)}(?![a-z])", name):
                return part
    return None


def _find_drum_parts(output_paths: Sequence[Path]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in output_paths:
        part = _part_for_filename(path.name)
        if part is not None:
            if part in found:
                raise RuntimeError(f"Drum separator returned multiple files for {part}.")
            found[part] = path

    missing = sorted(set(DRUM_PARTS) - set(found))
    if missing:
        raise RuntimeError(
            "Drum separator did not produce all expected parts "
            f"({', '.join(missing)}); found: {', '.join(sorted(found)) or 'none'}."
        )
    return found


def _check_alignment(reference: Path, stems: dict[str, Path]) -> None:
    import soundfile as sf

    reference_info = sf.info(reference)
    misaligned: list[str] = []
    for name, path in stems.items():
        info = sf.info(path)
        if info.samplerate != reference_info.samplerate or info.frames != reference_info.frames:
            misaligned.append(
                f"{name} ({info.samplerate} Hz, {info.frames} frames)"
            )
    if misaligned:
        expected = f"{reference_info.samplerate} Hz, {reference_info.frames} frames"
        raise RuntimeError(
            f"Separated stems are not aligned with {reference.name} ({expected}): "
            + ", ".join(misaligned)
        )


def _output_names(input_path: Path) -> dict[str, str]:
    prefix = input_path.stem
    names = {
        f"demucs_{stem}": f"{prefix}_demucs_{stem}.wav"
        for stem in DEMUCS_STEMS
    }
    names.update(
        {
            f"mdx23c_{part}": f"{prefix}_mdx23c_{part}.wav"
            for part in DRUM_PARTS
        }
    )
    return names


def separate(input_path: Path, overwrite: bool = False) -> list[Path]:
    input_path = validate_input(input_path)
    output_names = _output_names(input_path)
    output_paths = {key: PROJECT_ROOT / name for key, name in output_names.items()}
    existing = [path for path in output_paths.values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Output files already exist; use --overwrite to replace them: "
            + ", ".join(path.name for path in existing)
        )

    with tempfile.TemporaryDirectory(prefix=".ailoop-", dir=PROJECT_ROOT) as temporary:
        work_dir = Path(temporary)
        demucs_command = [
            sys.executable,
            "-m",
            "demucs.separate",
            "--name",
            DEMUCS_MODEL,
            "--out",
            str(work_dir / "demucs"),
            str(input_path),
        ]
        print("Separating mix with Demucs...")
        subprocess.run(demucs_command, check=True)

        demucs_stems = _find_demucs_outputs(work_dir / "demucs", input_path.stem)
        _check_alignment(demucs_stems["drums"], demucs_stems)

        drum_output_dir = work_dir / "mdx23c"
        drum_output_dir.mkdir()
        DRUMSEP_MODEL_CACHE.mkdir(parents=True, exist_ok=True)

        from audio_separator.separator import Separator

        separator = Separator(
            model_file_dir=str(DRUMSEP_MODEL_CACHE),
            output_dir=str(drum_output_dir),
            output_format="WAV",
        )
        separator.load_model(model_filename=DRUMSEP_MODEL)
        print("Separating Demucs drum stem into kit parts...")
        separator_filenames = separator.separate(str(demucs_stems["drums"]))
        drum_parts = _find_drum_parts(
            _resolve_separator_outputs(drum_output_dir, separator_filenames)
        )
        _check_alignment(demucs_stems["drums"], drum_parts)

        source_paths = {
            **{f"demucs_{name}": path for name, path in demucs_stems.items()},
            **{f"mdx23c_{name}": path for name, path in drum_parts.items()},
        }
        staged_paths: dict[str, Path] = {}
        for key, source in source_paths.items():
            staged = work_dir / output_names[key]
            shutil.copy2(source, staged)
            staged_paths[key] = staged

        for key, staged in staged_paths.items():
            staged.replace(output_paths[key])

    return list(output_paths.values())


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        outputs = separate(args.input, overwrite=args.overwrite)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Error: Demucs exited with status {error.returncode}.", file=sys.stderr)
        return error.returncode or 1

    print("Created:")
    for path in outputs:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
