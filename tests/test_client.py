"""Tests for the OpenAlex API client."""

from unittest.mock import MagicMock

import httpx
import pytest

from src.openalex_mcp.client import OpenAlexClient


class TestOpenAlexClient:
    """Test the OpenAlex API client."""

    def test_init_default_values(self):
        """Test client initialization with default values."""
        client = OpenAlexClient()
        assert client.email is None
        assert client.timeout == 30.0  # from config
        assert client._client is None

    def test_init_custom_values(self):
        """Test client initialization with custom values."""
        client = OpenAlexClient(email="test@example.com", timeout=60.0)
        assert client.email == "test@example.com"
        assert client.timeout == 60.0

    def test_build_url_basic(self):
        """Test URL building without parameters."""
        client = OpenAlexClient()
        url = client._build_url("works")
        assert url == "https://api.openalex.org/works"

    def test_build_url_with_email(self):
        """Test URL building with email parameter."""
        client = OpenAlexClient(email="test@example.com")
        url = client._build_url("works")
        assert "mailto=test%40example.com" in url

    def test_build_url_with_params(self):
        """Test URL building with query parameters."""
        client = OpenAlexClient()
        params = {"search": "machine learning", "page": 1}
        url = client._build_url("works", params)
        assert "search=machine+learning" in url
        assert "page=1" in url

    def test_build_url_strip_leading_slash(self):
        """Test URL building strips leading slash from endpoint."""
        client = OpenAlexClient()
        url = client._build_url("/works")
        assert url == "https://api.openalex.org/works"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        client = OpenAlexClient()

        async with client as c:
            assert c is client
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

        # Client should be closed after context exit
        assert client._client.is_closed

    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_httpx_client, sample_work_data):
        """Test successful API request."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_work_data
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient(email="test@example.com")
        client._client = mock_httpx_client

        result = await client._make_request("works/W123")

        assert result == sample_work_data
        mock_httpx_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, mock_httpx_client):
        """Test API request with HTTP error."""
        # Setup mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        error = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=mock_response
        )
        mock_httpx_client.get.side_effect = error

        client = OpenAlexClient()
        client._client = mock_httpx_client

        with pytest.raises(Exception) as exc_info:
            await client._make_request("works/nonexistent")

        assert "OpenAlex API error (404)" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_network_error(self, mock_httpx_client):
        """Test API request with network error."""
        error = httpx.RequestError("Connection failed")
        mock_httpx_client.get.side_effect = error

        client = OpenAlexClient()
        client._client = mock_httpx_client

        with pytest.raises(Exception) as exc_info:
            await client._make_request("works")

        assert "Request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_without_client(self):
        """Test making request without initialized client."""
        client = OpenAlexClient()

        with pytest.raises(RuntimeError) as exc_info:
            await client._make_request("works")

        assert "Client not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_works_single(self, mock_httpx_client, sample_work_data):
        """Test getting a single work by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_work_data
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        result = await client.get_works(work_id="W123")

        assert result == sample_work_data
        # Verify the correct endpoint was called
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "works/W123" in called_url

    @pytest.mark.asyncio
    async def test_get_works_search(self, mock_httpx_client, sample_search_response):
        """Test searching works."""
        sample_search_response["results"] = [{"id": "W123", "title": "Test Work"}]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        result = await client.get_works(
            search="machine learning",
            sort="cited_by_count",
            page=2,
            per_page=50
        )

        assert result == sample_search_response
        # Verify parameters were included
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "search=machine+learning" in called_url
        assert "sort=cited_by_count" in called_url
        assert "page=2" in called_url
        assert "per_page=50" in called_url

    @pytest.mark.asyncio
    async def test_get_works_with_filters(self, mock_httpx_client, sample_search_response):
        """Test searching works with filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        filter_params = {
            "publication_year": ">=2020",
            "is_oa": "true"
        }

        result = await client.get_works(
            search="AI",
            filter_params=filter_params,
            select=["id", "title", "cited_by_count"]
        )

        assert result == sample_search_response
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "filter=" in called_url
        assert "select=id%2Ctitle%2Ccited_by_count" in called_url

    @pytest.mark.asyncio
    async def test_get_authors(self, mock_httpx_client, sample_author_data):
        """Test getting author by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_author_data
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        result = await client.get_authors(author_id="A123")

        assert result == sample_author_data
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "authors/A123" in called_url

    @pytest.mark.asyncio
    async def test_get_institutions(self, mock_httpx_client, sample_institution_data):
        """Test getting institution by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_institution_data
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        result = await client.get_institutions(institution_id="I123")

        assert result == sample_institution_data
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "institutions/I123" in called_url

    @pytest.mark.asyncio
    async def test_get_sources(self, mock_httpx_client, sample_source_data):
        """Test getting source by ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_source_data
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        result = await client.get_sources(source_id="S123")

        assert result == sample_source_data
        called_url = mock_httpx_client.get.call_args[0][0]
        assert "sources/S123" in called_url

    @pytest.mark.asyncio
    async def test_pagination_limits(self, mock_httpx_client, sample_search_response):
        """Test that pagination limits are enforced."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_search_response
        mock_httpx_client.get.return_value = mock_response

        client = OpenAlexClient()
        client._client = mock_httpx_client

        # Request more than max per page (200)
        await client.get_works(search="test", per_page=300)

        called_url = mock_httpx_client.get.call_args[0][0]
        # Should be capped at 200
        assert "per_page=200" in called_url

    @pytest.mark.asyncio
    async def test_rate_limiting_semaphore(self):
        """Test that rate limiting semaphore is properly configured."""
        client = OpenAlexClient()

        # Verify semaphore is created with correct value from config
        assert client._rate_limiter._value == 10  # default from config
