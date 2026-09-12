"""Command-line interface."""

from __future__ import annotations

import argparse

from .config import load_config
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="indnet")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run the configured analysis")
    run.add_argument("--config", required=True, help="path to a TOML configuration")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        destination = run_pipeline(load_config(args.config))
        print(f"Wrote association edges to {destination}")
        return 0
    raise AssertionError("unreachable")
