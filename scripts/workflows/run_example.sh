#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repository_root"

python scripts/examples/generate_synthetic_data.py
python -m indnet run --config configs/example.toml
