# Release checklist

- [ ] Confirm the repository was initialized from this clean directory, not copied
      from a repository with legacy history.
- [ ] Confirm only source, tests, documentation, and safe configuration examples
      are staged.
- [ ] Run the unit tests.
- [ ] Run the release auditor with all locally required deny tokens.
- [ ] Confirm `core.hooksPath` points to `.githooks` in the release clone.
- [ ] Review `git diff --cached --stat` and `git diff --cached`.
- [ ] Confirm no real data, metadata mappings, logs, notebooks, results, or figures
      appear in `git ls-files`.
- [ ] Have a second person perform disclosure review.
- [ ] Select and approve a software license.
- [ ] Configure branch protection and secret scanning on the hosting platform.
- [ ] Tag the reviewed commit rather than an unreviewed working tree.

Suggested initialization:

```bash
git init
git add .
python scripts/quality/audit_release.py
git diff --cached --stat
```

Do not add the old repository as an ancestor or merge its history into this clean
release.
