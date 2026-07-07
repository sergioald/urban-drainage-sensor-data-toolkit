# Security review

## Summary

The uploaded code contained hard-coded operational credentials and endpoints. Those are not suitable for a public GitHub repository. This converted repository uses a sanitized archive and a separate public-safe package.

## Actions performed

- Redacted email addresses.
- Redacted IPv4 addresses and FTP host strings.
- Redacted common password, user, and spreadsheet-ID assignments.
- Removed logs, binaries, temporary files, backup database files, private CSV exports, and the old `TO_REMOVE/` tree.
- Added `.gitignore` patterns for tokens, credential files, local data, logs, binaries, and private outputs.
- Excluded `the removed private legacy archive` from linting to avoid treating preserved historical scripts as modern maintained package code.

## Before publishing

Run a dedicated secret scanner such as GitHub secret scanning, gitleaks, or trufflehog on the final repository. Also review the sanitized legacy archive manually if the repository will be made public.

## Important

Do not commit the original ZIP, the original unredacted scripts, `.pickle` tokens, OAuth credential JSON files, FTP credentials, or real operational CSV exports.
