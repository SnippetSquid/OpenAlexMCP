# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenAlex MCP Server is a Model Context Protocol (MCP) server that provides access to the OpenAlex scholarly database containing 240M+ works, authors, institutions, and other academic entities. The project is built as an async Python application using FastMCP, httpx, and Pydantic.

## Development Commands

### Installation and Setup
```bash
pip install -e .                    # Install package
pip install -e ".[dev,test]"        # Install with dev dependencies
```

### Testing
```bash
make test-unit                      # Unit tests only (no network)
make test                           # All tests including integration
make test-cov                       # Tests with coverage report
pytest -m "not integration and not slow"  # Skip integration tests
python run_tests.py --type unit    # Alternative test runner
```

### Code Quality
```bash
make lint                          # Run ruff and black checks
make format                        # Format code with black and ruff
make type-check                    # Run mypy type checking
make ci                           # Run all CI checks (lint, type, unit tests)
```

### Running the Server
```bash
openalex-mcp                      # Run MCP server (via entry point)
python -m src.openalex_mcp.server # Alternative server startup
make run-server                   # Via Makefile
```

## Architecture

### Core Components

- **`server.py`**: FastMCP server implementation with tool routing
- **`client.py`**: Async OpenAlex API client with rate limiting and error handling
- **`tools.py`**: MCP tool definitions and implementations for all 7 tools
- **`config.py`**: Environment-based configuration management
- **`models.py`**: Pydantic data models for API responses
- **`logutil.py`**: Logging configuration

### MCP Tools Available

1. `search_works` - Search scholarly works with filters (author, year, venue, topic, OA)
2. `search_authors` - Search researchers with metrics filtering
3. `search_institutions` - Search academic institutions by country/type
4. `search_sources` - Search journals/conferences with publisher filtering  
5. `get_work_details` - Get detailed work info by ID/DOI
6. `get_author_profile` - Get author profile by ID/ORCID
7. `get_citations` - Find works citing a specific work

### Key Design Patterns

- **Async Context Manager**: OpenAlexClient uses `async with` for proper resource cleanup
- **Rate Limiting**: Semaphore-based concurrent request limiting (default 10)
- **Error Handling**: Comprehensive HTTP error handling with meaningful messages
- **Configuration**: Environment variable-based config with validation
- **Formatting**: Structured text output formatting for all entity types

### Environment Configuration

Optional environment variables:
- `OPENALEX_EMAIL`: Real email for polite pool access and higher rate limits (optional - works fine without)
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `LOG_API_REQUESTS`: true/false for request debugging
- `OPENALEX_TIMEOUT`: Request timeout in seconds (default: 30.0)
- `OPENALEX_MAX_CONCURRENT`: Max concurrent requests (default: 10)

**Important**: If setting `OPENALEX_EMAIL`, use a real email address. OpenAlex rejects obvious test emails (like `test@example.com`) with 400 errors. The server works perfectly without any email configured.

### Testing Strategy

- **Unit Tests**: Mock HTTP responses, no network required (`pytest -m "not integration"`)
- **Integration Tests**: Real API calls, marked with `@pytest.mark.integration` and `@pytest.mark.slow`
- **Coverage**: Configured for branch coverage with HTML reports in `htmlcov/`
- **Test Fixtures**: Centralized in `conftest.py` for mock responses and test data

## Common Development Workflows

When adding new functionality:
1. Add/modify tool definitions in `tools.py` 
2. Update client methods in `client.py` if needed
3. Add corresponding tests in `tests/`
4. Run `make ci` to verify lint, types, and unit tests
5. Test integration with `make test-integration` if network changes made

When debugging API issues:
1. Set `LOG_API_REQUESTS=true` and `LOG_LEVEL=DEBUG`
2. Check rate limiting and timeout settings
3. Verify OpenAlex API response format hasn't changed
4. Ensure all search endpoints use `search` parameter (not `q`)
5. Check filter syntax follows OpenAlex format: `attribute:value`
6. For year ranges, use `from_publication_date` and `to_publication_date` when both bounds needed
7. If getting 400 "Invalid" errors, check if `OPENALEX_EMAIL` is set to a test/fake email - unset it or use a real email