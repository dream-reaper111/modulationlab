from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

from modulationlab.core import analyze, load
from modulationlab.cli import main


class Tests(unittest.TestCase):
    def test_features(self):
        samples = np.exp(2j * np.pi * 4000 * np.arange(4096) / 100_000).astype(np.complex64)
        report = analyze(samples, 100_000)
        self.assertAlmostEqual(report["frequency_offset_estimate_hz"], 4000, delta=1)
        self.assertEqual(report["classification_confidence"], "low")
        self.assertIsNone(report["symbol_rate_estimate"])

    def test_formats_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)
            samples = np.ones(1024, dtype=np.complex64)
            samples.tofile(p / "iq.bin")
            self.assertEqual(len(load(p / "iq.bin", "cf32le", 100000)[0]), 1024)
            self.assertEqual(main([str(p / "iq.bin"), "--format", "cf32le", "--sample-rate", "100000", "--output", str(p / "out.json")]), 0)
            with wave.open(str(p / "iq.wav"), "wb") as stream:
                stream.setnchannels(2)
                stream.setsampwidth(2)
                stream.setframerate(100000)
                stream.writeframes(np.zeros(2048, dtype="<i2").tobytes())
            self.assertEqual(len(load(p / "iq.wav", "wav-iq", None)[0]), 1024)
            (p / "bad.bin").write_bytes(b"abc")
            with self.assertRaises(ValueError):
                load(p / "bad.bin", "cs16le", 100000)


if __name__ == "__main__":
    unittest.main()
