# Scripts

Scripts are grouped by responsibility. They contain no source-specific ingestion,
column mappings, participant records, or derived research output.

```text
examples/     Generate deterministic artificial inputs for documentation
quality/      Audit candidate release files for disclosure hazards
workflows/    Run documented, source-independent analysis workflows
release/      Verify tests, audit checks, and package construction
```

Reusable analysis logic belongs in `src/indnet/`; scripts should remain thin
entry points. Real source adapters and private configuration belong in controlled
storage outside this repository.
