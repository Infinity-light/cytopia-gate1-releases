from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEPLOY_WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"


def require(source: str, phrase: str) -> None:
    if phrase not in source:
        raise AssertionError(f"missing static cutover contract: {phrase}")


def main() -> None:
    source = DEPLOY_WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.safe_load(source)
    if not isinstance(workflow, dict) or "jobs" not in workflow:
        raise AssertionError("deploy workflow is not valid YAML")

    forbidden = (
        "docker build -f " + "runner/",
        "cytopia-runner:" + "$SOURCE_SHA",
        "/var/run/" + "docker.sock",
        "DEPLOYMENT_" + "RUNNER_TOKEN",
        "DEPLOYMENT_" + "MYSQL_ROOT_PASSWORD",
        "DEPLOYMENT_" + "POSTGRES_PASSWORD",
        "Full-stack " + "runner smoke",
    )
    for phrase in forbidden:
        if phrase in source:
            raise AssertionError(f"retired dynamic deployment behavior remains: {phrase}")

    for phrase in (
        "Build static control-plane image",
        "docker save \"cytopia-gate1:$SOURCE_SHA\"",
        "static-cutover-$SOURCE_SHA.containers",
        "label=cytopia.release",
        "docker update --restart=no",
        "docker compose up -d --no-build cytopia-gate1",
        "A student runtime container is still running",
        "Production E2E",
    ):
        require(source, phrase)

    print("static release workflow contract passed")


if __name__ == "__main__":
    main()
