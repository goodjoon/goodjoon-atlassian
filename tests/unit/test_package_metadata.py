from pathlib import Path

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


def test_cli_version_uses_goodjoon_atlassian_program_name() -> None:
    """Verify the Click CLI reports the published command name."""
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("goodjoon-atlassian, version ")
