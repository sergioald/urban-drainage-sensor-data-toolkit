# Portfolio summary

This repository shows how an operational folder of legacy monitoring scripts can be converted into a public-safe research-software artefact.

The original code base focused on practical urban drainage telemetry tasks: importing field files, merging point-level CSV exports, checking timestamps, preparing reports, handling rainfall/pluviometer information, and moving processed files between local folders and external systems. The public repository does not expose the original infrastructure. Instead, it separates reusable logic from private operational dependencies.

## What it demonstrates

- Engineering-data QA/QC for semi-structured time-series CSV exports.
- Timestamp parsing from Italian-style `DATA` / `ORA` columns.
- Duplicate-timestamp handling and missing-row estimates.
- Simple last-contact status checks for monitoring points.
- Daily aggregation of level, velocity, flow, battery, and rainfall-like channels.
- Reproducible public examples using synthetic data.
- Responsible publication of legacy code through sanitisation and documentation.

## Reviewer takeaway

The important point is not that every historical script is now a modern package. The important point is that a real engineering monitoring workflow has been translated into a clear, reviewable, public-safe repository with tests, docs, examples, a CLI, and explicit confidentiality boundaries.
