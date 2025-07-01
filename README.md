# OpenAlex MCP Server

A Model Context Protocol (MCP) server that provides access to the OpenAlex scholarly database containing 240M+ works, authors, institutions, and other academic entities.

## Features

- **Comprehensive Search**: Search across works, authors, institutions, and publication venues
- **Detailed Profiles**: Get detailed information about specific works, authors, and institutions
- **Citation Analysis**: Track citations and find related works
- **Rich Metadata**: Access comprehensive scholarly data including affiliations, topics, and metrics
- **Open Access Focus**: Filter for open access publications and venues
- **No Authentication Required**: Free access to the complete OpenAlex database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
```

2. Install the package:
```bash
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

Add to your Claude Desktop configuration:

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

```bash
git clone https://github.com/your-username/openalex-mcp.git
cd openalex-mcp
pip install -e ".[dev]"
```

### Run Tests

The project includes a comprehensive test suite with unit tests, integration tests, and coverage reporting.

#### Quick Test Commands

```bash
# Run unit tests only (fast, no network required)
make test-unit

# Run all tests including integration tests (requires network)
make test

# Run tests with coverage report
make test-cov

# Run linting and type checking
make lint
make type-check
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

#### Test Types

- **Unit Tests**: Fast tests that don't require network access, use mocked API responses
- **Integration Tests**: Tests against the real OpenAlex API (marked as `slow` and `integration`)
- **Coverage Tests**: Unit tests with code coverage reporting

#### Test Structure

```
tests/
├── conftest.py          # Pytest configuration and fixtures
├── test_client.py       # OpenAlex API client tests
├── test_tools.py        # MCP tools functionality tests
├── test_server.py       # MCP server tests
├── test_config.py       # Configuration management tests
├── test_models.py       # Pydantic model tests
├── test_logging.py      # Logging functionality tests
└── test_integration.py  # Integration tests (network required)
```

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

```bash
black src/
ruff check src/
mypy src/
```

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

## Support

- **Documentation**: [OpenAlex API Documentation](https://docs.openalex.org/)
- **Issues**: [GitHub Issues](https://github.com/your-username/openalex-mcp/issues)
- **OpenAlex**: [OpenAlex Website](https://openalex.org/)

## Citation

If you use OpenAlex data in your research, please cite:

Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833