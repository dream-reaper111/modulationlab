# Architecture

The bounded loader validates IQ encoding and sample rate. NumPy computes amplitude, phase difference, and segmentation; SciPy Welch computes relative PSD. A deliberately low-confidence rule maps a small set of features to candidate ASK/OOK, FSK/GFSK/PSK, or QAM/ASK families. This is an investigation aid, not a modulation decoder. No shared runtime dependency or transmitter code exists.
