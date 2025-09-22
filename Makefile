.PHONY: mcp-run
mcp-run:
	@ZK_DIR=. uv run mcp dev src/zk_utils/presentation/mcp/server.py

.PHONY: format
format:
	@uv run ruff check . --select I --fix-only --exit-zero
	@uv run ruff format .

.PHONY: lint
lint:
	@uv run ruff check .
	@uv run mypy --show-error-codes .

.PHONY: test
test:
	@uv run pytest

.PHONY: build
build:
	@uv build --refresh --no-cache

.PHONY: pre-commit
pre-commit: format lint test build
