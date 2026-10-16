# AILoop

AILoop is a local command-line prototype for separating audio loops. The first
prototype focuses on drum-kit extraction.

## Requirements

- Python 3.10 or newer
- `ffmpeg` available on `PATH` for MP3 decoding
- Several gigabytes of free disk space for Python dependencies and model weights

Install the Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

Run from any working directory; output WAV files are written into this project
directory:

```bash
python3 script.py --input /path/to/loop.mp3
```

The first run downloads model weights and can take some time. The default
Demucs model is `htdemucs_ft`; the Demucs drum stem is then split with the
MDX23C DrumSep model.

There is no fixed 10-second minimum: shorter valid audio is processed too.
For useful drum separation, provide at least one complete loop; a 4-bar loop
(about 7–8 seconds at 120–140 BPM) is a good starting point. MDX23C uses its
short-audio processing path for inputs under 10 seconds. The full input is
processed; it is not truncated to the 16-second limit used by one online demo.

For an input named `loop.mp3`, the command creates:

```text
loop_demucs_drums.wav
loop_demucs_bass.wav
loop_demucs_other.wav
loop_demucs_vocals.wav
loop_mdx23c_kick.wav
loop_mdx23c_snare.wav
loop_mdx23c_toms.wav
loop_mdx23c_hihat.wav
loop_mdx23c_ride.wav
loop_mdx23c_crash.wav
```

Existing outputs are not replaced by default. Pass `--overwrite` to replace
outputs with the same input prefix.

## Prototype limitations

- Demucs is used here to obtain its drum stem; its other stems are retained as
  intermediate outputs. The prototype does not yet create a dedicated synth
  stem.
- DrumSep separates into six model outputs. As with any source-separation
  model, bleed and audio artifacts may remain; perfectly clean or click-free
  separation cannot be guaranteed.
- The script checks that output stems have the same sample rate and frame count
  so they stay time-aligned. It does not add gain normalization or fades.
- The MDX23C checkpoint is downloaded by `audio-separator` on first use and is
  cached under `~/.cache/ailoop/models`.
- The MDX23C checkpoint's redistribution and commercial-use terms should be
  confirmed before distributing this prototype or using it commercially.
