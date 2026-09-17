# Jarvis automation

This repository contains reviewed, reusable GitHub Actions workflows for the
Jarvis project. It is public because GitHub permits a public caller repository
to use reusable workflows only from public repositories. It contains no
credentials, infrastructure identifiers, deployment environments, or cloud
authentication.

## Reusable workflow

`.github/workflows/jarvis-ci.yml` provides the stable Jarvis validation suite:

- Python linting, typing, ownership checks, and tests;
- Terraform formatting, validation, and native tests;
- Packer template validation;
- filesystem, secret, dependency, and infrastructure scanning; and
- clean GCP, AWS, and Azure image builds, smoke tests, SBOMs, and scans.

Only `joshuamyers22/jarvis` is accepted by the workflow's runtime caller
allowlist. All workflow and job token permissions are `contents: read`; the
workflow declares no secrets, OIDC permission, environment, registry login, or
publishing step. GitHub prevents a called workflow from elevating beyond its
caller's token, and the repository policy check rejects changes that weaken
these controls.

Callers must pin a full commit SHA:

```yaml
permissions:
  contents: read

jobs:
  validation:
    uses: joshuamyers22/jarvis-automation/.github/workflows/jarvis-ci.yml@COMMIT_SHA
    permissions:
      contents: read
```

Moving branches and tags are not accepted production references. Updating the
pin requires a reviewed pull request in the caller after this repository's
policy workflow succeeds.

## Change procedure

1. Modify the reusable workflow without adding caller-controlled shell inputs.
2. Run `python3 scripts/check_workflow_policy.py`.
3. Open a pull request and require the `workflow-policy` check, an up-to-date
   branch, and resolved review threads. Direct pushes, force-pushes, and branch
   deletion are blocked with no bypass actors.
4. Merge, record the resulting commit SHA, and update callers to that exact SHA.
5. Confirm an allowlisted caller succeeds and an unlisted test repository fails
   in `authorize caller` before relying on the new revision.

Cloud OIDC, registry credentials, protected environments, release approvals,
deployment, and rollback stay in their owning repositories. They must never be
added here.

`CODEOWNERS` records current ownership. The personal-account repository cannot
require independent approval while it has only one maintainer; enable required
code-owner approval as soon as a second trusted maintainer or organization team
exists. Until then, immutable downstream pins ensure no automation change is
adopted by Jarvis without a separate reviewed Jarvis change.
