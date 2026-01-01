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

.PHONY: update-pre-commit
update-pre-commit:
	@uv run pre-commit autoupdate

.PHONY: mcp-run
mcp-run:
	@ZK_DIR=. uv run mcp dev src/zk_utils/presentation/mcp/server.py

# Docker関連の変数
DOCKER_USERNAME ?= koeikajihome
DOCKER_IMAGE = zk-utils-mcp
VERSION = $(shell uv version --short)
DOCKER_TAG ?= latest

.PHONY: docker-login
docker-login:
	@docker login

.PHONY: docker-build
docker-build:
	@docker build -t $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG) .
	@docker tag $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(VERSION)

.PHONY: docker-push
docker-push:
	@docker push $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	@docker push $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(VERSION)

.PHONY: docker-all
docker-all: docker-build docker-push

.PHONY: docker-run
docker-run:
	@docker run -it --rm \
		-v $(ZK_NOTES_DIR):/zk-notes:ro \
		$(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG)

.PHONY: docker-compose-up
docker-compose-up:
	@docker compose up

.PHONY: docker-compose-down
docker-compose-down:
	@docker compose down
