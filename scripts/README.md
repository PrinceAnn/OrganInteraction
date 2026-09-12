# Scripts

Scripts are grouped by responsibility. They contain no source-specific ingestion,
column mappings, participant records, or derived research output.

```text
associations/  Fit linear or binary outcome models with optional covariates
decomposition/ Compute principal-component scores and loadings
examples/     Generate deterministic artificial inputs for documentation
genetics/     Format local association output to a neutral exchange schema
networks/     Build pairwise association edge tables
quality/      Audit candidate release files for disclosure hazards
reports/      Create compact summaries from generated edge tables
workflows/    Run documented, source-independent analysis workflows
release/      Verify tests, audit checks, and package construction
visualization/ Render generated network edge tables
```

Reusable analysis logic belongs in `src/indnet/`; scripts should remain thin
entry points. Real source adapters and private configuration belong in controlled
storage outside this repository.
