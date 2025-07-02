# OpenAlex MCP Server

A Model Context Protocol (MCP) server that provides access to the OpenAlex scholarly database containing 240M+ works, authors, institutions, and other academic entities.

**Status**: ✅ All 127 tests passing | 🚀 Production ready | 📊 Full test coverage

## Features

- **Comprehensive Search**: Search across works, authors, institutions, and publication venues
- **Detailed Profiles**: Get detailed information about specific works, authors, and institutions
- **Citation Analysis**: Track citations and find related works
- **Rich Metadata**: Access comprehensive scholarly data including affiliations, topics, and metrics
- **Open Access Focus**: Filter for open access publications and venues
- **No Authentication Required**: Free access to the complete OpenAlex database
- **FastMCP Architecture**: Built with the latest FastMCP framework for optimal performance
- **Robust Error Handling**: Comprehensive error handling and logging for production use
- **Async Support**: Full async/await support for high-performance concurrent requests

## Installation

### Option 1: From PyPI (Recommended)
```bash
# Install with uv (recommended)
uv add openalex-mcp

# Or install with pip
pip install openalex-mcp
```

### Option 2: From Source with uv
```bash
# Clone and install with uv
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
uv sync

# Run tests
uv run pytest tests/ -v
```

### Option 3: From Source with pip
```bash
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
pip install -e .
```

## Configuration

### Environment Variables

- `OPENALEX_EMAIL`: Your email address (recommended for polite pool access and higher rate limits)
- `OPENALEX_TIMEOUT`: Request timeout in seconds (default: 30.0)
- `OPENALEX_MAX_CONCURRENT`: Maximum concurrent requests (default: 10)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_API_REQUESTS`: Log API requests for debugging (default: false)

### Example Configuration

```bash
export OPENALEX_EMAIL="your.email@example.com"
export LOG_LEVEL="DEBUG"
export LOG_API_REQUESTS="true"
```

## Usage

### Running the MCP Server

```bash
openalex-mcp
```

### Available Tools

#### 1. `search_works`
Search for scholarly works (papers, articles, books, datasets).

**Parameters:**
- `query` (required): Search query for works
- `author`: Filter by author name
- `year_from`: Filter works from this year onwards
- `year_to`: Filter works up to this year
- `venue`: Filter by venue/journal name
- `topic`: Filter by research topic/field
- `open_access`: Filter for open access works only
- `sort`: Sort order (`relevance_score`, `cited_by_count`, `publication_date`)
- `limit`: Number of results (max 50, default 10)

**Example:**
```json
{
  "query": "machine learning",
  "year_from": 2020,
  "open_access": true,
  "sort": "cited_by_count",
  "limit": 10
}
```

#### 2. `search_authors`
Search for authors and researchers.

**Parameters:**
- `query` (required): Search query for author names
- `institution`: Filter by institution name
- `topic`: Filter by research area/topic
- `h_index_min`: Minimum h-index
- `works_count_min`: Minimum number of works
- `sort`: Sort order (`relevance_score`, `cited_by_count`, `works_count`, `h_index`)
- `limit`: Number of results (max 50, default 10)

#### 3. `search_institutions`
Search for academic institutions.

**Parameters:**
- `query` (required): Search query for institution names
- `country`: Filter by country code (e.g., 'US', 'GB', 'CA')
- `type`: Filter by institution type
- `works_count_min`: Minimum number of works
- `sort`: Sort order (`relevance_score`, `cited_by_count`, `works_count`)
- `limit`: Number of results (max 50, default 10)

#### 4. `search_sources`
Search for journals, conferences, and publication venues.

**Parameters:**
- `query` (required): Search query for source names
- `type`: Filter by source type (`journal`, `conference`, `repository`, etc.)
- `publisher`: Filter by publisher name
- `open_access`: Filter for open access sources only
- `works_count_min`: Minimum number of works published
- `sort`: Sort order (`relevance_score`, `cited_by_count`, `works_count`, `h_index`)
- `limit`: Number of results (max 50, default 10)

#### 5. `get_work_details`
Get detailed information about a specific work.

**Parameters:**
- `work_id` (required): OpenAlex work ID or DOI

#### 6. `get_author_profile`
Get detailed profile information about a specific author.

**Parameters:**
- `author_id` (required): OpenAlex author ID or ORCID

#### 7. `get_citations`
Get works that cite a specific work for citation analysis.

**Parameters:**
- `work_id` (required): OpenAlex work ID or DOI of the work to find citations for
- `sort`: Sort order (`publication_date`, `cited_by_count`, `relevance_score`)
- `limit`: Number of citing works (max 50, default 20)

## Integration with MCP Clients

### Claude Desktop

#### Option 1: Using uv run (Recommended for development)
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "OpenAlexMCP": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/openalex-mcp",
        "openalex-mcp"
      ],
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  }
}
```

#### Option 2: Using uvx (For published package)
```json
{
  "mcpServers": {
    "OpenAlexMCP": {
      "command": "uvx",
      "args": [
        "openalex-mcp"
      ],
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  }
}
```

#### Option 3: Traditional pip installation
```json
{
  "mcpServers": {
    "OpenAlexMCP": {
      "command": "openalex-mcp",
      "env": {
        "OPENALEX_EMAIL": "your.email@example.com"
      }
    }
  }
}
```

### Continue.dev

Add to your Continue configuration:

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

## Development

### Setup Development Environment

#### With uv (Recommended)
```bash
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
uv sync --group dev
```

#### With pip
```bash
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
pip install -e ".[dev]"
```

### Run Tests

The project includes a comprehensive test suite with **127 passing tests** covering unit tests, integration tests, and full code coverage.

#### Quick Test Commands

##### With uv (Recommended)
```bash
# Run all tests
uv run pytest tests/ -v

# Run unit tests only (fast, no network required)
uv run pytest tests/ -m "not slow and not integration" -v

# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test files
uv run pytest tests/test_client.py -v
uv run pytest tests/test_tools.py -v
```

##### With pip/Python
```bash
# Run all tests (recommended)
python -m pytest tests/ -v

# Run unit tests only (fast, no network required)  
python -m pytest tests/ -m "not slow and not integration" -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

#### Using the Test Runner Script

```bash
# Install dependencies and run unit tests
python run_tests.py --install-deps --type unit

# Run with linting and formatting
python run_tests.py --lint --format --type unit

# Run coverage tests
python run_tests.py --type coverage

# Run integration tests (requires network)
python run_tests.py --type integration
```

#### Current Test Status: ✅ 127/127 Tests Passing

All tests have been recently updated and fixed to work with the current FastMCP server implementation.

#### Test Types

- **Unit Tests**: Fast tests that don't require network access, use mocked API responses
- **Integration Tests**: Tests against the real OpenAlex API (marked as `slow` and `integration`)
- **Coverage Tests**: Unit tests with code coverage reporting

#### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_client.py       # OpenAlex API client tests (19 tests)
├── test_tools.py        # MCP tools functionality tests (33 tests)
├── test_server.py       # FastMCP server tests (10 tests) 
├── test_config.py       # Configuration management tests (13 tests)
├── test_models.py       # Pydantic model tests (26 tests)
├── test_logging.py      # Logging functionality tests (17 tests)
└── test_integration.py  # Integration tests (9 tests, network required)
```

#### Recent Test Fixes

The test suite has been comprehensively updated to fix all issues:

- ✅ **Server Tests**: Updated for FastMCP architecture with `@mcp.tool()` decorators
- ✅ **Logging Tests**: Fixed caplog capture with temporary logger propagation 
- ✅ **Integration Tests**: Removed fake emails causing API 400 errors
- ✅ **Config Tests**: Fixed module import consistency for dynamic config
- ✅ **API Parameters**: Fixed invalid field names for OpenAlex API compatibility
- ✅ **Sort Parameters**: Updated default sort from problematic `relevance_score` to `cited_by_count`
- ✅ **All Dependencies**: Updated for latest FastMCP and async patterns

#### Running Specific Tests

```bash
# Run only client tests
pytest tests/test_client.py

# Run tests matching a pattern
pytest -k "search_works"

# Run with verbose output
pytest -v

# Skip integration tests
pytest -m "not integration and not slow"
```

### Code Formatting

#### With uv
```bash
uv run black src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
```

#### With pip/Python
```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

### Building and Packaging

#### With uv (Recommended)
```bash
# Build source distribution and wheel
uv build

# This creates:
# - dist/openalex_mcp-1.0.0.tar.gz
# - dist/openalex_mcp-1.0.0-py3-none-any.whl
```

#### Package Contents Verification
```bash
# Check source distribution contents
tar -tzf dist/openalex_mcp-1.0.0.tar.gz

# Check wheel contents  
unzip -l dist/openalex_mcp-1.0.0-py3-none-any.whl
```

For detailed packaging instructions, see [PACKAGING.md](PACKAGING.md).

## Rate Limits and Best Practices

- **Daily Limit**: 100,000 requests per day per user
- **Polite Pool**: Add your email address to get better performance and higher rate limits
- **Concurrent Requests**: Limited to 10 concurrent requests by default
- **Pagination**: Use pagination for large result sets
- **Caching**: Results are not cached by default - implement caching in your application if needed

## OpenAlex Data Coverage

- **240M+ Works**: Journal articles, books, datasets, theses
- **Global Coverage**: ~2x coverage compared to traditional databases
- **Author Disambiguation**: Advanced author name disambiguation
- **Institution Mapping**: Comprehensive institution identification
- **Open Access**: Full open access status and location information
- **Citation Networks**: Complete citation relationships
- **Research Topics**: AI-powered topic classification

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

#### 400 "Invalid" API Errors
- **Cause**: Using fake email addresses (like `test@example.com`) with OpenAlex API
- **Solution**: Either omit the email entirely or use a real email address
- **Note**: Email is optional but provides better rate limits when valid

#### MCP JSON Protocol Errors
- **Cause**: Logger outputting to stdout instead of stderr
- **Status**: ✅ **FIXED** - Logger now correctly outputs to stderr
- **Context**: This was causing "Unexpected non-whitespace character after JSON" errors

#### Test Failures
- **Status**: ✅ **FIXED** - All 127 tests now pass
- **Recent Fixes**:
  - Updated server tests for FastMCP architecture
  - Fixed logging test capture with proper propagation
  - Resolved config import inconsistencies
  - Updated integration tests to avoid API errors

#### Import Errors
- **Cause**: Module import path inconsistencies
- **Status**: ✅ **FIXED** - All imports use consistent relative paths
- **Solution**: Client now uses relative imports (`.config`, `.logutil`)

#### API Parameter Errors (403 "Invalid query parameters")
- **Cause**: Using outdated field names like `author.display_name.search`
- **Status**: ✅ **FIXED** - Updated to correct API field names
- **Solution**: Now uses `raw_author_name.search` and `cited_by_count` sort default

#### Sort Parameter Errors (403 "Sorting relevance score ascending is not allowed")
- **Cause**: OpenAlex API doesn't allow ascending sort on `relevance_score`
- **Status**: ✅ **FIXED** - Changed default sort to `cited_by_count`
- **Solution**: Users can still specify `relevance_score` but it uses default sort order

### Development Tips

```bash
# Verify all tests pass
python -m pytest tests/ -v

# Check for any import issues
python -c "from src.openalex_mcp.server import mcp; print('✅ All imports working')"

# Test the server manually
python -m src.openalex_mcp.server
```

## Support

- **Documentation**: [OpenAlex API Documentation](https://docs.openalex.org/)
- **Issues**: [GitHub Issues](https://github.com/your-username/openalex-mcp/issues)
- **OpenAlex**: [OpenAlex Website](https://openalex.org/)

## Citation

If you use OpenAlex data in your research, please cite:

Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833