# Hardware support

Run `python3 -m modulationlab.cli hardware` for local capability reporting. Adapter sysfs presence is not proof of usable hardware.

Offline import works without equipment. No BLE adapter, dedicated sniffer, or SDR device is connected by this utility. GNU Radio is not required or integrated. Sample rate is an operator-supplied file attribute and does not assert a receiver's hardware capabilities. No live RF tests were performed.
