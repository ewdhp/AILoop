import unittest
from pathlib import Path

import script


class DrumOutputNamingTests(unittest.TestCase):
    def test_output_names_have_input_prefix_and_all_stages(self) -> None:
        names = script._output_names(Path("/audio/melodic-loop.mp3"))

        self.assertEqual(
            names["demucs_drums"],
            "melodic-loop_demucs_drums.wav",
        )
        self.assertEqual(
            names["mdx23c_hihat"],
            "melodic-loop_mdx23c_hihat.wav",
        )
        self.assertEqual(len(names), 10)

    def test_separator_stem_names_map_to_six_parts(self) -> None:
        files = [
            Path("loop_(Kick).wav"),
            Path("loop_(Snare).wav"),
            Path("loop_(Toms).wav"),
            Path("loop_(HH).wav"),
            Path("loop_(Ride).wav"),
            Path("loop_(Crash).wav"),
        ]

        parts = script._find_drum_parts(files)

        self.assertEqual(set(parts), set(script.DRUM_PARTS))


if __name__ == "__main__":
    unittest.main()
