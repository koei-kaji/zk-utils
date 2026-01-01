# Stage 1: Build zk from source
FROM golang:1.25-alpine AS zk-builder

# Install dependencies for building zk
RUN apk add --no-cache git make build-base

# Clone and build zk
RUN git clone https://github.com/zk-org/zk.git /tmp/zk && \
    cd /tmp/zk && \
    make && \
    cp zk /usr/local/bin/zk

# Stage 2: Final image with Python and MCP server
FROM python:3.12-slim-bookworm

# Copy zk binary from builder stage
COPY --from=zk-builder /usr/local/bin/zk /usr/local/bin/zk

# Copy uv and uvx from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./
COPY src ./src

# Install dependencies (production only, no dev dependencies)
ENV UV_NO_DEV=1
RUN uv sync --frozen

# Set environment variables
# ZK_DIR should be mounted as a volume at runtime
ENV ZK_DIR=/zk-notes
ENV PATH="/app/.venv/bin:$PATH"

# Create default zk notes directory
RUN mkdir -p /zk-notes

# Expose stdio for MCP server (MCP uses stdio transport, not network ports)
# This is a documentation-only directive
EXPOSE 0

# Run MCP server using uv
CMD ["sh", "-c", "zk index && uv run zk-utils-mcp"]
