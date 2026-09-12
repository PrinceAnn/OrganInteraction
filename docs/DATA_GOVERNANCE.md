# Data governance

This repository follows a source-only publication model. Research data and
source-specific metadata belong in controlled storage, not in Git.

## Never commit

- participant-level or row-level research tables;
- source data dictionaries, field mappings, coding tables, or linkage keys;
- raw, cleaned, imputed, or derived datasets;
- summary-statistic exports unless separately approved for public release;
- analysis logs, crash dumps, serialized sessions, notebook outputs, or archives;
- figures and tables derived from restricted records unless disclosure review has
  explicitly approved them;
- local configuration containing real column names, storage paths, or identifiers.

## Safe development pattern

1. Store input outside the repository or under `local-data/`.
2. Put private configuration in `configs/local.toml`.
3. Write generated files under `local-results/`.
4. Use artificial data for tests and examples.
5. Run `python tools/audit_release.py` before staging changes.
6. Inspect the exact staged set with `git diff --cached --name-only`.

`.gitignore` reduces accidental additions but is not a security boundary. A file
already committed remains in Git history even after it is deleted from the latest
revision. If restricted material ever entered history, stop publication and have
the repository owner perform a coordinated history rewrite and credential review.
