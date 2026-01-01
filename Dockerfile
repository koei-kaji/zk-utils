# Stage 1: Build zk from source
FROM golang:1.25-bookworm AS zk-builder

# Install dependencies for building zk
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends git make build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone and build zk
WORKDIR /tmp/zk
RUN git clone https://github.com/zk-org/zk.git . && \
    make && \
    cp zk /usr/local/bin/zk

# Stage 2: Final image with Python and MCP server
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Upgrade pip and create non-root user
RUN pip install --no-cache-dir --upgrade pip==25.3 && \
    useradd -m -u 1000 app

# Install build dependencies for Rust packages
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy zk binary from builder stage
COPY --from=zk-builder /usr/local/bin/zk /usr/local/bin/zk

# Set working directory for application
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./
COPY src ./src

# Install dependencies and change ownership
ENV UV_NO_DEV=1
RUN uv sync --frozen && \
    chown -R app:app /app

# Create zk-notes directory for mounting
RUN mkdir -p /zk-notes && chown app:app /zk-notes

# Remove build dependencies to reduce image size
RUN apt-get purge -y --auto-remove build-essential

# Set environment variables
# ZK_DIR should be mounted as a volume at runtime
ENV ZK_DIR=/zk-notes
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER app

# Metadata labels for Docker Hub
ARG VERSION
LABEL org.opencontainers.image.title="zk-utils-mcp"
LABEL org.opencontainers.image.description="MCP server for zk note management with search, linking, and organization tools"
LABEL org.opencontainers.image.source="https://github.com/koei-kaji/zk-utils"
LABEL org.opencontainers.image.version="$VERSION"
LABEL org.opencontainers.image.authors="koei-kaji <koei.kaji@gmail.com>"
LABEL org.opencontainers.image.url="https://github.com/koei-kaji/zk-utils"
LABEL org.opencontainers.image.documentation="https://github.com/koei-kaji/zk-utils/blob/main/README.md"

# Expose stdio for MCP server (MCP uses stdio transport, not network ports)
# This is a documentation-only directive
EXPOSE 0

# Run MCP server using uv
CMD ["uv", "run", "zk-utils-mcp"]
