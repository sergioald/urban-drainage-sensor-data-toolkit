# Confidentiality statement

This repository is designed as a public-safe representation of a historical operational monitoring code base.

The following items are intentionally not included:

- live credentials, passwords, tokens, OAuth files, or spreadsheet secrets;
- private operational CSV exports;
- private validation samples;
- generated private audit/report outputs;
- runtime logs;
- backup database files;
- executable binaries such as browser drivers;
- temporary download folders;
- historical duplicate folders marked for removal.

Sanitized legacy scripts may still contain historical variable names, path conventions, client/system labels, and domain-specific terminology because these are needed to preserve code traceability. They should be reviewed again before any public release connected to a specific company or client.

The tested package under `src/` uses synthetic examples and does not connect to external private services.

The `audit` command and `tools/make_private_sample.py` are intended for local/private use. Their outputs can still contain sensitive file names, column names, asset names, links, coordinates, or identifiers. Do not commit those outputs unless they have been manually anonymised.
