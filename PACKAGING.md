# OpenAlex MCP - uv Packaging Guide

This document explains how to package and distribute the OpenAlex MCP server using [uv](https://docs.astral.sh/uv/).

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.10 or higher

## Quick Start

### 1. Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd openalex-mcp

# Sync dependencies with uv
uv sync --group dev

# Run tests
uv run pytest tests/ -v

# Run the server
uv run openalex-mcp
```

### 2. Building the Package

```bash
# Build both source distribution and wheel
uv build

# This creates:
# - dist/openalex_mcp-1.0.0.tar.gz (source distribution)
# - dist/openalex_mcp-1.0.0-py3-none-any.whl (wheel)
```

### 3. Installing the Package

```bash
# Install from wheel (recommended)
uv add openalex_mcp-1.0.0-py3-none-any.whl

# Or install from source
uv add openalex_mcp-1.0.0.tar.gz

# Or install from PyPI (when published)
uv add openalex-mcp
```

## Package Structure

```
openalex-mcp/
├── pyproject.toml          # Package configuration
├── uv.lock                 # Dependency lock file
├── MANIFEST.in             # Additional files to include
├── src/openalex_mcp/       # Source code
├── tests/                  # Test suite
└── dist/                   # Built packages
```

## Configuration

### pyproject.toml

The package is configured using `pyproject.toml` with:

- **Build system**: Hatchling
- **Python requirement**: >=3.10 (required by MCP)
- **Dependencies**: MCP, httpx, pydantic, anyio
- **Entry point**: `openalex-mcp` command
- **Dev dependencies**: pytest, black, ruff, mypy

### Dependency Groups

```toml
[dependency-groups]
dev = ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black>=23.0.0", ...]
test = ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-cov>=4.0.0"]
```

## Development Workflow

### 1. Installing Dependencies

```bash
# Install production dependencies only
uv sync

# Install with development dependencies
uv sync --group dev

# Install with test dependencies
uv sync --group test
```

### 2. Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test groups
uv run pytest tests/ -m "not slow and not integration"

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### 3. Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### 4. Building and Testing

```bash
# Build the package
uv build

# Verify package contents
tar -tzf dist/openalex_mcp-1.0.0.tar.gz
unzip -l dist/openalex_mcp-1.0.0-py3-none-any.whl
```

## Publishing

### 1. To Test PyPI

```bash
# Build first
uv build

# Upload to Test PyPI
uv publish --repository testpypi dist/*
```

### 2. To PyPI

```bash
# Build first
uv build

# Upload to PyPI
uv publish dist/*
```

## Installation for Users

### 1. From PyPI (when published)

```bash
# Install in current environment
uv add openalex-mcp

# Install globally
uv tool install openalex-mcp

# Run directly without installing
uvx openalex-mcp
```

### 2. From Source

```bash
# Install from Git repository
uv add git+https://github.com/your-username/openalex-mcp.git

# Install from local source
uv add ./path/to/openalex-mcp
```

## MCP Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openalex": {
      "command": "openalex-mcp",
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  }
}
```

### Continue.dev

Add to Continue configuration:

```json
{
  "mcpServers": [
    {
      "name": "openalex",
      "command": ["openalex-mcp"],
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  ]
}
```

## Environment Variables

- `OPENALEX_EMAIL`: Your email for OpenAlex API (optional but recommended)
- `OPENALEX_TIMEOUT`: Request timeout in seconds (default: 30)
- `OPENALEX_MAX_CONCURRENT`: Max concurrent requests (default: 10)
- `LOG_LEVEL`: Logging level (default: INFO)

## Troubleshooting

### 1. Python Version Issues

```bash
# Check Python version
python --version

# uv requires Python 3.10+ for MCP compatibility
```

### 2. Dependency Conflicts

```bash
# Clear uv cache
uv cache clean

# Reinstall dependencies
rm uv.lock
uv sync
```

### 3. Build Issues

```bash
# Clean build artifacts
rm -rf dist/ build/

# Rebuild
uv build
```

## Package Verification

### 1. Check Package Contents

```bash
# Source distribution
tar -tzf dist/openalex_mcp-1.0.0.tar.gz

# Wheel
unzip -l dist/openalex_mcp-1.0.0-py3-none-any.whl
```

### 2. Test Installation

```bash
# Create test environment
mkdir test-env && cd test-env
uv init --no-readme

# Install package
uv add ../dist/openalex_mcp-1.0.0-py3-none-any.whl

# Test command
uv run openalex-mcp
```

### 3. Verify Entry Points

```bash
# Check entry points in wheel
unzip -p dist/openalex_mcp-1.0.0-py3-none-any.whl openalex_mcp-1.0.0.dist-info/entry_points.txt
```

## Package Metadata

The package includes:

- **Name**: openalex-mcp
- **Version**: 1.0.0
- **Description**: MCP server for OpenAlex scholarly database
- **License**: MIT
- **Python Support**: 3.10+
- **Keywords**: mcp, openalex, scholarly, research, academic
- **Entry Point**: `openalex-mcp` command

## Additional Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [OpenAlex API Documentation](https://docs.openalex.org/)
- [Python Packaging Guide](https://packaging.python.org/)