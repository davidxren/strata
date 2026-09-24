import argparse
from collections.abc import Sequence
from pathlib import Path

DEFAULT_SAMPLES = 100_000
DEFAULT_DATA_DIR = Path("data")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="strata")
    commands = parser.add_subparsers(dest="command", required=True)
    bench = commands.add_parser("bench", help="bytes per sample against the baselines")
    bench.add_argument("--out", type=Path, help="also write the report to this file")
    bench.add_argument(
        "--samples", type=int, default=DEFAULT_SAMPLES, help="samples per synthetic dataset"
    )
    bench.add_argument(
        "--data", type=Path, default=DEFAULT_DATA_DIR, help="directory of real exports as CSV"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "bench":
        from bench.run import run

        run(args.samples, args.data, args.out)
        return 0
    parser.error(f"unknown command {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
