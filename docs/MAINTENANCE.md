# Maintenance guide

## Every change

1. Work on a short-lived branch created from an up-to-date `main` branch.
2. Keep real data, source mappings, and local configuration outside Git.
3. Add or update tests with artificial inputs.
4. Run the release auditor before staging.
5. Review the staged diff, including file names, before committing.
6. Use a pull request and require CI plus disclosure review before merging.

## Local safeguards

Enable the tracked hooks in every clone:

```bash
git config core.hooksPath .githooks
```

Store project-specific deny tokens only in local Git configuration:

```bash
git config --local --add indnet.restrictedToken "$RESTRICTED_SOURCE_TOKEN"
```

The pre-commit hook runs the source disclosure audit. The pre-push hook repeats
the audit and runs all tests.

## Dependency maintenance

- Review supported Python versions and minimum dependency versions quarterly.
- Let automated dependency updates run through the same tests and review process.
- Do not accept lockfiles generated from private package indexes if they disclose
  internal host names or credentials.

## Release routine

1. Complete `docs/RELEASE_CHECKLIST.md`.
2. Update the package version in `pyproject.toml` and `src/indnet/__init__.py`.
3. Build and test the wheel in a clean environment.
4. Tag the reviewed merge commit using a semantic version such as `v0.1.0`.
5. Publish only artifacts built from that tag.

## Suspected disclosure

Stop pushes and follow `SECURITY.md`. Do not attempt an uncoordinated force-push:
removing restricted material from distributed Git history requires repository
owners, data stewards, and anyone holding a clone to coordinate.
