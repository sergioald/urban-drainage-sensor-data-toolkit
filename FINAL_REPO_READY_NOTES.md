# Final repository handoff notes

This repository package is the public-ready conversion of the original PVS codebase.

## What informed this conversion

The public package structure and documentation were refined using a private review of representative files from the original workflow, including samples from:

- `INPUT/`
- `DATA/`
- `REPORT/TABELLE`
- `REPORT/LOG`
- `REPORT/GRAFICI`
- `REPORT/STATISTICA/ANNUALE`
- representative `OUTPUT/CURVE` plot images

No private original data files were copied into the public repository.

## What the repo is ready for

- Public GitHub release as a portfolio/research-software repository
- Demonstration of the workflow structure and software engineering approach
- Local use with private data through documented private workflows
- Future refactoring toward a cleaner package API

## Recommended public release boundary

Safe to publish:

- package source code in `src/`
- tests
- documentation
- synthetic examples
- tooling for auditing and sampling private data

Do not publish:

- original `INPUT/`, `DATA/`, `REPORT/`, `OUTPUT/` folders
- credentials, tokens, or pickles
- exact map files, coordinates, or client/project identifiers
- raw private sample archives

## Remaining optional future improvements

These are optional and do not block publication:

1. Replace most of `the removed private legacy archiveraw/` with a smaller curated subset.
2. Add richer synthetic fixtures that mimic the private `INPUT/DATA/REPORT/OUTPUT` structure.
3. Add log-parsing and graphics-inspection commands to the CLI.
4. Add one synthetic curve-plot example and one synthetic map example.
5. Add stronger publication-safety scanning for credentials, paths, and coordinates.

## Publication recommendation

The repository is suitable to publish now as a cleaned, documented, public-facing conversion, with the understanding that it is a structured and safer research-software/portfolio release rather than a full public release of the original operational dataset and outputs.

## Final applied-AI addition

A lightweight optional applied-AI extension has been added before publication:

- transparent sensor-health feature extraction
- robust anomaly scoring baseline
- synthetic anomaly-screening example
- tests for ML feature extraction and anomaly scoring
- documentation in `docs/applied_ai_extension.md`

This is intentionally positioned as an explainable baseline, not as a validated
production ML model.
