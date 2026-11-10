import argparse
import hashlib
import json
from pathlib import Path
import sys
from .hardware import capabilities
import wave

from .core import analyze, load


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["hardware"]:
        print(json.dumps(capabilities(), indent=2))
        return 0
    parser = argparse.ArgumentParser(prog="modulationlab")
    parser.add_argument("input", type=Path)
    parser.add_argument("--format", choices=["cf32le", "cs16le", "wav-iq"], required=True)
    parser.add_argument("--sample-rate", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        samples, rate = load(args.input, args.format, args.sample_rate)
        report = analyze(samples, rate)
        report["source_sha256"] = hashlib.sha256(args.input.read_bytes()).hexdigest()
        report["format"] = args.format
        result = json.dumps(report) + "\n"
        if args.output:
            args.output.write_text(result)
        else:
            print(result, end="")
        return 0
    except (OSError, ValueError, EOFError, wave.Error) as exc:
        print(f"modulationlab: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
