# ModulationLab

ModulationLab performs bounded offline IQ feature analysis. It imports interleaved `cf32le`, `cs16le`, and stereo 16-bit PCM WAV IQ; reports frequency offset, Welch PSD, amplitude variability, frequency deviation indicator, active segments, and a low-confidence modulation candidate. It does not reconstruct messages, decrypt communications, or transmit.

```sh
python3 -m modulationlab.cli authorized.iq --format cf32le --sample-rate 1000000 --output report.json
```

IQ input is capped at 32 MB. Any candidate is heuristic and may be wrong; symbol rate remains unestimated when evidence is insufficient. See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [HARDWARE.md](HARDWARE.md), [DEPENDENCIES.md](DEPENDENCIES.md), and [VALIDATION_REPORT.md](VALIDATION_REPORT.md).
