.PHONY: format
format:
	@uv run ruff check . --select I --fix-only --exit-zero
	@uv run ruff format .

.PHONY: lint
lint:
	@uv run ruff check .
	@uv run mypy --show-error-codes .
	@uv run ty check .

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
DOCKER_USERNAME ?= koeikajidev
DOCKER_IMAGE = zk-utils-mcp
VERSION = $(shell uv version --short)
DOCKER_TAG ?= latest
DOCKLE_LATEST=$$( \
  curl --silent "https://api.github.com/repos/goodwithtech/dockle/releases/latest" | \
  grep '"tag_name":' | \
  sed -E 's/.*"v([^"]+)".*/\1/' \
)
TRIVY_LATEST=$$( \
  curl --silent "https://api.github.com/repos/aquasecurity/trivy/releases/latest" | \
  grep '"tag_name":' | \
  sed -E 's/.*"v([^"]+)".*/\1/' \
)

.PHONY: docker-login
docker-login:
	@docker login

.PHONY: docker-lint
docker-lint:
	@hadolint ./Dockerfile

.PHONY: docker-build
docker-build:
	@docker build --build-arg VERSION=$(VERSION) -t $(DOCKER_IMAGE):$(VERSION) .

.PHONY: docker-scan
docker-scan:
	@docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		goodwithtech/dockle:v$(DOCKLE_LATEST) --no-color -af settings.py $(DOCKER_IMAGE):$(VERSION)
	@docker run -v /var/run/docker.sock:/var/run/docker.sock \
		-v $${HOME}/Library/Caches:/root/.cache/ \
		aquasec/trivy:$(TRIVY_LATEST) image --ignore-unfixed $(DOCKER_IMAGE):$(VERSION)

.PHONY: docker-check
docker-check: docker-lint docker-build docker-scan

.PHONY: docker-push
docker-push: docker-check
	@docker tag $(DOCKER_IMAGE):$(VERSION) $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(VERSION)
	@docker tag $(DOCKER_IMAGE):$(VERSION) $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG)
	@docker push $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(VERSION)
	@docker push $(DOCKER_USERNAME)/$(DOCKER_IMAGE):$(DOCKER_TAG)
