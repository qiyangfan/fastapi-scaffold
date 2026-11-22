from pathlib import Path

from scripts import license_check


def test_normalize_expression_handles_aliases_and_operators() -> None:
    assert license_check._normalize_expression("MIT License") == ["MIT"]
    assert license_check._normalize_expression("Apache-2.0 OR MIT") == ["Apache-2.0", "MIT"]


def test_production_names_filters_comments_and_extras(tmp_path: Path) -> None:
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("# comment\nfastapi==0.1\nuvicorn[standard]==0.1\n\n", encoding="utf-8")

    assert license_check._production_names(requirements) == {"fastapi", "uvicorn"}


def test_project_name_reads_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "fastapi_scaffold"\nversion = "0"\n', encoding="utf-8")

    assert license_check._project_name(pyproject) == "fastapi-scaffold"
