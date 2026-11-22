.PHONY: sync setup lint format-check typecheck pylint imports deps dead licenses secrets markdownlint infra-lint test audit gates run

sync:
	uv sync --frozen

setup:
	uv sync
	uv run pre-commit install --install-hooks

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy

pylint:
	uv run pylint --disable=all --enable=too-many-lines,too-many-public-methods,too-many-locals,too-many-return-statements,too-many-statements,too-many-ancestors,too-many-boolean-expressions,cyclic-import,E --disable=E1101 --jobs=0 src/app tests scripts

imports:
	uv run lint-imports

deps:
	uv run deptry src

dead:
	uv run vulture src --min-confidence 100

licenses:
	@tmp=$$(mktemp); trap 'rm -f "$$tmp"' EXIT; uv export --no-dev --format requirements-txt --no-hashes > "$$tmp"; uv run python scripts/license_check.py "$$tmp"

secrets:
	@if command -v gitleaks >/dev/null 2>&1; then gitleaks dir . --redact --exit-code 1; else echo "[secrets] gitleaks 未安装,跳过"; fi

markdownlint:
	npx --yes markdownlint-cli2@0.24.1

infra-lint:
	@if command -v actionlint >/dev/null 2>&1; then actionlint; else echo "[infra-lint] actionlint 未安装,跳过"; fi
	@if command -v hadolint >/dev/null 2>&1; then hadolint Dockerfile; else echo "[infra-lint] hadolint 未安装,跳过"; fi
	@if command -v uvx >/dev/null 2>&1; then uvx yamllint==1.38.0 -c .yamllint.yml .github; else echo "[infra-lint] uvx 未安装,跳过 yamllint"; fi

test:
	uv run pytest -q --cov --cov-branch --cov-report=term-missing --cov-fail-under=70

# 安全与供应链：需要 registry，CI security.yml 同款
audit:
	uv run --with pip-audit==2.10.1 pip-audit --local

gates: lint format-check typecheck pylint imports deps dead licenses secrets markdownlint infra-lint test

run:
	uv run uvicorn app.main:app --reload --port 3000
