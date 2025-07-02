"""Tests for the OpenAlex MCP FastMCP server."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.openalex_mcp.server import mcp


@pytest.mark.asyncio
async def test_list_tools():
    """Test that all expected tools are registered."""
    tools = await mcp.list_tools()
    assert len(tools) == 8

    tool_names = [tool.name for tool in tools]
    expected_tools = [
        "OpenAlex_search_works",
        "OpenAlex_search_authors",
        "OpenAlex_search_institutions",
        "OpenAlex_search_sources",
        "OpenAlex_get_work_details",
        "OpenAlex_get_author_profile",
        "OpenAlex_get_citations",
        "OpenAlex_download_paper"
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_search_works_tool():
    """Test search_works_tool function."""
    with patch('src.openalex_mcp.server.search_works', new_callable=AsyncMock) as mock_search:
        from src.openalex_mcp.server import OpenAlex_search_works

        # Mock the search_works function to return expected format
        mock_search.return_value = [MagicMock(text="Mock search result")]

        result = await OpenAlex_search_works("machine learning", limit=5)

        assert result == "Mock search result"
        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_authors_tool():
    """Test search_authors_tool function."""
    with patch('src.openalex_mcp.server.search_authors', new_callable=AsyncMock) as mock_search:
        from src.openalex_mcp.server import OpenAlex_search_authors

        mock_search.return_value = [MagicMock(text="Mock author result")]

        result = await OpenAlex_search_authors("John Doe", limit=5)

        assert result == "Mock author result"
        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_institutions_tool():
    """Test search_institutions_tool function."""
    with patch('src.openalex_mcp.server.search_institutions', new_callable=AsyncMock) as mock_search:
        from src.openalex_mcp.server import OpenAlex_search_institutions

        mock_search.return_value = [MagicMock(text="Mock institution result")]

        result = await OpenAlex_search_institutions("Stanford", country="US")

        assert result == "Mock institution result"
        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_sources_tool():
    """Test search_sources_tool function."""
    with patch('src.openalex_mcp.server.search_sources', new_callable=AsyncMock) as mock_search:
        from src.openalex_mcp.server import OpenAlex_search_sources

        mock_search.return_value = [MagicMock(text="Mock source result")]

        result = await OpenAlex_search_sources("Nature", source_type="journal")

        assert result == "Mock source result"
        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_work_details_tool():
    """Test get_work_details_tool function."""
    with patch('src.openalex_mcp.server.get_work_details', new_callable=AsyncMock) as mock_get:
        from src.openalex_mcp.server import OpenAlex_get_work_details

        mock_get.return_value = [MagicMock(text="Mock work details")]

        result = await OpenAlex_get_work_details("W123456789")

        assert result == "Mock work details"
        mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_author_profile_tool():
    """Test get_author_profile_tool function."""
    with patch('src.openalex_mcp.server.get_author_profile', new_callable=AsyncMock) as mock_get:
        from src.openalex_mcp.server import OpenAlex_get_author_profile

        mock_get.return_value = [MagicMock(text="Mock author profile")]

        result = await OpenAlex_get_author_profile("A123456789")

        assert result == "Mock author profile"
        mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_citations_tool():
    """Test get_citations_tool function."""
    with patch('src.openalex_mcp.server.get_citations', new_callable=AsyncMock) as mock_get:
        from src.openalex_mcp.server import OpenAlex_get_citations

        mock_get.return_value = [MagicMock(text="Mock citations")]

        result = await OpenAlex_get_citations("W123456789", sort="cited_by_count")

        assert result == "Mock citations"
        mock_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_tool_with_exception():
    """Test tool behavior when underlying function raises exception."""
    with patch('src.openalex_mcp.server.search_works', new_callable=AsyncMock) as mock_search:
        from src.openalex_mcp.server import OpenAlex_search_works

        mock_search.side_effect = Exception("Test error")

        # The tool doesn't handle exceptions - they bubble up
        with pytest.raises(Exception, match="Test error"):
            await OpenAlex_search_works("test query")

        mock_search.assert_awaited_once()


@pytest.mark.asyncio
async def test_tool_call_via_mcp():
    """Test calling tools through the MCP interface."""
    with patch('src.openalex_mcp.server.search_works', new_callable=AsyncMock) as mock_search:
        # Mock successful response
        mock_search.return_value = [MagicMock(text="Mock result")]

        # Test that we can call tools through the FastMCP interface
        result = await mcp.call_tool("OpenAlex_search_works", {"query": "test"})

        # FastMCP returns a tuple: (content, structured_content)
        assert isinstance(result, tuple)
        assert len(result) == 2
        content, structured = result
        assert len(content) == 1
        assert content[0].text == "Mock result"
