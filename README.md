# indNet

`indNet` is a small, configuration-driven toolkit for building association
networks from continuous traits. It provides reusable steps for numeric data
validation, rank-based inverse normal transformation, covariate residualization,
pairwise association testing, and false-discovery-rate control.

This repository is a source-only release. It contains no participant-level
records, source data dictionaries, cohort-specific mappings, analysis outputs,
or derived figures. The example workflow generates artificial data locally at
runtime; generated files are ignored by Git.

## Repository layout

```text
configs/              Safe example configuration using artificial column names
docs/                 Data-governance and release guidance
src/indnet/           Installable Python package
tests/                Unit and end-to-end tests
tools/                Synthetic-data generator and release auditor
.github/workflows/    Continuous integration checks
```

## Quick start

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python tools/generate_synthetic_data.py
python -m indnet run --config configs/example.toml
```

The example writes an edge table to `local-results/`. Both the generated input
and output directories are excluded from version control.

Run the test and publication checks before every release:

```bash
python -m unittest discover -s tests -v
python tools/audit_release.py
```

The repository includes version-controlled Git hooks. Enable them once per local
clone:

```bash
git config core.hooksPath .githooks
```

For an additional project-specific content check, provide one or more restricted
source identifiers without storing them in the repository:

```bash
python tools/audit_release.py --deny-token "$RESTRICTED_SOURCE_TOKEN"
```

Maintainers can persist the same token only in local Git metadata. It will not be
part of commits or clones:

```bash
git config --local --add indnet.restrictedToken "$RESTRICTED_SOURCE_TOKEN"
```

## Input contract

The analysis input is a local CSV or TSV table with:

- one unique sample identifier column;
- at least two numeric trait columns; and
- zero or more numeric covariate columns.

Column selection lives in a TOML configuration file. Keep real configurations
outside the repository or name them `configs/local*.toml` so Git ignores them.
Never place source-system identifiers or real data dictionary entries in tracked
configuration.

## Scope

This release focuses on the reusable statistical core. Cohort ingestion,
identifier linkage, source-specific quality-control rules, and downstream export
to third-party analysis services are deliberately excluded because those steps
depend on restricted metadata.

## License

No reuse license is granted yet. Add the license approved by the project owners
before advertising the repository as open source.

See [the maintenance guide](docs/MAINTENANCE.md) for the routine review and
release workflow.
