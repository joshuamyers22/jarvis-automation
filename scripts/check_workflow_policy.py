#!/usr/bin/env python3
"""Fail when reusable workflow changes broaden the automation trust boundary."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
REUSABLE_WORKFLOW = WORKFLOW_DIR / "jarvis-ci.yml"
ALLOWED_CALLERS = ("joshuamyers22/jarvis",)
ACTION_REFERENCE = re.compile(r"^[ \t]*(?:-[ \t]+)?uses:[ \t]+([^\s#]+)", re.MULTILINE)
WRITE_PERMISSION = re.compile(r"^[ \t]+[a-z-]+:[ \t]+write[ \t]*$", re.MULTILINE)
SECRET_REFERENCE = re.compile(r"\$\{\{[ \t]*secrets\.")


def workflow_paths() -> list[Path]:
    return sorted([*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")])


def require(source: str, marker: str, path: Path) -> None:
    if marker not in source:
        raise SystemExit(f"{path}: missing required policy marker: {marker}")


def forbid(source: str, marker: str, path: Path) -> None:
    if marker in source:
        raise SystemExit(f"{path}: forbidden workflow capability: {marker}")


def check_reusable_workflow() -> None:
    source = REUSABLE_WORKFLOW.read_text()
    for marker in (
        "workflow_call:",
        "permissions:\n  contents: read",
        "Enforce the caller allowlist",
        "CALLER_REPOSITORY: ${{ github.repository }}",
        "persist-credentials: false",
    ):
        require(source, marker, REUSABLE_WORKFLOW)
    for caller in ALLOWED_CALLERS:
        require(source, f"{caller}) ;;", REUSABLE_WORKFLOW)

    for marker in (
        "id-token: write",
        "environment:",
        "secrets:",
        "${{ secrets.",
        "google-github-actions/auth@",
        "aws-actions/configure-aws-credentials@",
        "azure/login@",
        "docker/login-action@",
        "docker login",
        "docker push",
        "gcloud auth",
        "aws ecr",
        "az acr",
        "push: true",
    ):
        forbid(source, marker, REUSABLE_WORKFLOW)
    if WRITE_PERMISSION.search(source):
        raise SystemExit(f"{REUSABLE_WORKFLOW}: write token permission is forbidden")
    if SECRET_REFERENCE.search(source):
        raise SystemExit(f"{REUSABLE_WORKFLOW}: secret references are forbidden")


def check_action_pins() -> None:
    full_sha = re.compile(r"^[^@]+@[0-9a-f]{40}$")
    for path in workflow_paths():
        for action in ACTION_REFERENCE.findall(path.read_text()):
            if not action.startswith("./") and not full_sha.fullmatch(action):
                raise SystemExit(f"{path}: action is not pinned to a full commit SHA: {action}")


def check_pull_request_workflows() -> None:
    trigger = re.compile(r"^[ \t]*pull_request(?:_target)?:", re.MULTILINE)
    for path in workflow_paths():
        source = path.read_text()
        if not trigger.search(source):
            continue
        require(source, "permissions:\n  contents: read", path)
        forbid(source, "pull_request_target:", path)
        if WRITE_PERMISSION.search(source):
            raise SystemExit(f"{path}: pull-request workflow has write permission")
        if SECRET_REFERENCE.search(source):
            raise SystemExit(f"{path}: pull-request workflow references a secret")


def main() -> None:
    paths = workflow_paths()
    if not paths:
        raise SystemExit("no workflow files found")
    check_reusable_workflow()
    check_action_pins()
    check_pull_request_workflows()
    print("workflow policy is valid")


if __name__ == "__main__":
    main()
