# Security policy

Report vulnerabilities through GitHub private vulnerability reporting. Do not
open a public issue containing credentials, private repository details, or an
exploit.

This repository must remain credential-free. Reusable workflows have read-only
repository access and must not request OIDC, consume secrets, enter environments,
authenticate to clouds or registries, or publish artifacts outside ordinary
GitHub Actions run artifacts. Action dependencies must use full commit SHAs.
