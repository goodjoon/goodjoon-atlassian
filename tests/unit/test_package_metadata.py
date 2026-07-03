import subprocess
import sys
from pathlib import Path

import yaml
from click.testing import CliRunner

from mcp_atlassian import main

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


def test_package_metadata_exposes_goodjoon_atlassian_cli() -> None:
    """Verify package metadata supports `uvx goodjoon-atlassian`."""
    pyproject_path = Path(__file__).parents[2] / "pyproject.toml"
    metadata = tomllib.loads(pyproject_path.read_text())

    assert metadata["project"]["name"] == "goodjoon-atlassian"
    assert metadata["project"]["scripts"]["goodjoon-atlassian"] == "mcp_atlassian:main"
    assert "authlib<1.7.0" in metadata["project"]["dependencies"]


def test_cli_version_uses_goodjoon_atlassian_program_name() -> None:
    """Verify the Click CLI reports the published command name."""
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("goodjoon-atlassian, version ")


def test_import_suppresses_fastmcp_authlib_jose_deprecation_warning() -> None:
    """Verify CLI startup does not show FastMCP's authlib.jose warning."""
    project_root = Path(__file__).parents[2]

    result = subprocess.run(
        [sys.executable, "-W", "default", "-c", "import mcp_atlassian"],
        cwd=project_root,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert "authlib.jose module is deprecated" not in result.stderr


def test_publish_workflow_targets_goodjoon_atlassian_with_trusted_publishing() -> None:
    """Verify release workflow publishes the forked PyPI package safely."""
    workflow_path = Path(__file__).parents[2] / ".github" / "workflows" / "publish.yml"
    workflow = yaml.safe_load(workflow_path.read_text())

    job = workflow["jobs"]["pypi-publish"]
    run_commands = [
        step["run"] for step in job["steps"] if isinstance(step, dict) and "run" in step
    ]

    assert job["environment"]["url"] == "https://pypi.org/p/goodjoon-atlassian"
    assert job["permissions"]["id-token"] == "write"
    assert "uv build --no-sources" in run_commands
    assert "uv publish --trusted-publishing always dist/*" in run_commands
    assert "PYPI_API_TOKEN" not in workflow_path.read_text()
