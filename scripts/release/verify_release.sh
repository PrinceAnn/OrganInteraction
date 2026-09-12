#!/bin/sh
set -eu

repository_root=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repository_root"

python scripts/quality/audit_release.py
PYTHONPATH=src python -m unittest discover -s tests -v
python -m pip wheel --no-deps --no-build-isolation --wheel-dir artifacts .
