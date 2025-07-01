"""Tests for the MCP tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from mcp.types import TextContent

from src.openalex_mcp.tools import (
    search_works,
    search_authors,
    search_institutions,
    search_sources,
    get_work_details,
    get_author_profile,
    get_citations,
    format_work_summary,
    format_author_summary,
    format_institution_summary,
    format_source_summary,
)


class TestToolFormatters:
    """Test the data formatting functions."""

    def test_format_work_summary(self, sample_work_data):
        """Test work summary formatting."""
        summary = format_work_summary(sample_work_data)
        
        assert "Attention Is All You Need" in summary
        assert "Ashish Vaswani" in summary
        assert "2017" in summary
        assert "15234" in summary  # citations
        assert "arXiv (Cornell University)" in summary
        assert "Machine Learning" in summary
        assert "W2741809807" in summary

    def test_format_work_summary_minimal_data(self):
        """Test work summary formatting with minimal data."""
        minimal_work = {
            "id": "W123",
            "title": "Test Paper",
            "publication_year": 2023,
            "cited_by_count": 5,
            "authorships": [],
            "topics": [],
            "primary_location": None
        }
        
        summary = format_work_summary(minimal_work)
        
        assert "Test Paper" in summary
        assert "2023" in summary
        assert "5" in summary
        assert "Unknown Venue" in summary
        assert "No topics" in summary

    def test_format_author_summary(self, sample_author_data):
        """Test author summary formatting."""
        summary = format_author_summary(sample_author_data)
        
        assert "Ashish Vaswani" in summary
        assert "0000-0003-4890-3406" in summary
        assert "Google" in summary
        assert "45" in summary  # works count
        assert "25000" in summary  # citations
        assert "32" in summary  # h-index
        assert "Machine Learning" in summary
        assert "A2208157607" in summary

    def test_format_institution_summary(self, sample_institution_data):
        """Test institution summary formatting."""
        summary = format_institution_summary(sample_institution_data)
        
        assert "Stanford University" in summary
        assert "education" in summary
        assert "US" in summary
        assert "125000" in summary  # works count
        assert "15000000" in summary  # citations
        assert "00f54p054" in summary  # ROR
        assert "http://www.stanford.edu/" in summary

    def test_format_source_summary(self, sample_source_data):
        """Test source summary formatting."""
        summary = format_source_summary(sample_source_data)
        
        assert "Nature" in summary
        assert "journal" in summary
        assert "Springer Nature" in summary
        assert "0028-0836" in summary  # ISSN
        assert "No" in summary  # Open Access = False
        assert "500000" in summary  # works count
        assert "S137773608" in summary


class TestSearchTools:
    """Test the search tool functions."""

    @pytest.mark.asyncio
    async def test_search_works_success(self, mock_openalex_client, sample_work_data, sample_search_response):
        """Test successful work search."""
        sample_search_response["results"] = [sample_work_data]
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "machine learning",
            "year_from": 2020,
            "sort": "cited_by_count",
            "limit": 10
        }
        
        results = await search_works(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert isinstance(results[0], TextContent)
        assert "Attention Is All You Need" in results[0].text
        assert "machine learning" in results[0].text
        
        # Verify client was called with correct parameters
        mock_openalex_client.get_works.assert_called_once()
        call_args = mock_openalex_client.get_works.call_args
        assert call_args.kwargs["search"] == "machine learning"
        assert call_args.kwargs["sort"] == "cited_by_count"
        assert call_args.kwargs["per_page"] == 10

    @pytest.mark.asyncio
    async def test_search_works_with_filters(self, mock_openalex_client, sample_search_response):
        """Test work search with filters."""
        sample_search_response["results"] = []
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "AI",
            "author": "John Doe",
            "venue": "Nature",
            "topic": "computer vision",
            "open_access": True,
            "year_from": 2020,
            "year_to": 2023
        }
        
        results = await search_works(mock_openalex_client, arguments)
        
        # Check that filters were passed correctly
        call_args = mock_openalex_client.get_works.call_args
        filter_params = call_args.kwargs["filter_params"]
        
        assert "author.display_name.search" in filter_params
        assert filter_params["author.display_name.search"] == "John Doe"
        assert "primary_location.source.display_name.search" in filter_params
        assert filter_params["primary_location.source.display_name.search"] == "Nature"
        assert "topics.display_name.search" in filter_params
        assert filter_params["topics.display_name.search"] == "computer vision"
        assert "is_oa" in filter_params
        assert filter_params["is_oa"] == "true"

    @pytest.mark.asyncio
    async def test_search_works_no_results(self, mock_openalex_client, sample_search_response):
        """Test work search with no results."""
        sample_search_response["results"] = []
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {"query": "nonexistent topic"}
        
        results = await search_works(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "No works found" in results[0].text
        assert "nonexistent topic" in results[0].text

    @pytest.mark.asyncio
    async def test_search_works_error(self, mock_openalex_client):
        """Test work search with API error."""
        mock_openalex_client.get_works = AsyncMock(side_effect=Exception("API Error"))
        
        arguments = {"query": "test"}
        
        results = await search_works(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Error searching works" in results[0].text
        assert "API Error" in results[0].text

    @pytest.mark.asyncio
    async def test_search_authors_success(self, mock_openalex_client, sample_author_data, sample_search_response):
        """Test successful author search."""
        sample_search_response["results"] = [sample_author_data]
        mock_openalex_client.get_authors = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "Ashish Vaswani",
            "institution": "Google",
            "h_index_min": 20
        }
        
        results = await search_authors(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Ashish Vaswani" in results[0].text
        assert "Google" in results[0].text
        
        # Verify filters
        call_args = mock_openalex_client.get_authors.call_args
        filter_params = call_args.kwargs["filter_params"]
        assert filter_params["last_known_institution.display_name.search"] == "Google"
        assert filter_params["h_index"] == ">=20"

    @pytest.mark.asyncio
    async def test_search_institutions_success(self, mock_openalex_client, sample_institution_data, sample_search_response):
        """Test successful institution search."""
        sample_search_response["results"] = [sample_institution_data]
        mock_openalex_client.get_institutions = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "Stanford",
            "country": "US",
            "type": "education"
        }
        
        results = await search_institutions(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Stanford University" in results[0].text
        
        # Verify filters
        call_args = mock_openalex_client.get_institutions.call_args
        filter_params = call_args.kwargs["filter_params"]
        assert filter_params["country_code"] == "US"
        assert filter_params["type"] == "education"

    @pytest.mark.asyncio
    async def test_search_sources_success(self, mock_openalex_client, sample_source_data, sample_search_response):
        """Test successful source search."""
        sample_search_response["results"] = [sample_source_data]
        mock_openalex_client.get_sources = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "Nature",
            "type": "journal",
            "open_access": False
        }
        
        results = await search_sources(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Nature" in results[0].text
        
        # Verify filters
        call_args = mock_openalex_client.get_sources.call_args
        filter_params = call_args.kwargs["filter_params"]
        assert filter_params["type"] == "journal"
        # open_access=False means no filter should be added
        assert "is_oa" not in filter_params


class TestDetailTools:
    """Test the detail retrieval tools."""

    @pytest.mark.asyncio
    async def test_get_work_details_success(self, mock_openalex_client, sample_work_data):
        """Test successful work detail retrieval."""
        mock_openalex_client.get_works = AsyncMock(return_value=sample_work_data)
        
        arguments = {"work_id": "W2741809807"}
        
        results = await get_work_details(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Attention Is All You Need" in results[0].text
        assert "https://doi.org/10.48550/arxiv.1706.03762" in results[0].text
        
        # Verify correct ID was used
        mock_openalex_client.get_works.assert_called_once_with(work_id="W2741809807")

    @pytest.mark.asyncio
    async def test_get_work_details_doi_format(self, mock_openalex_client, sample_work_data):
        """Test work detail retrieval with DOI input."""
        mock_openalex_client.get_works = AsyncMock(return_value=sample_work_data)
        
        arguments = {"work_id": "10.48550/arxiv.1706.03762"}
        
        results = await get_work_details(mock_openalex_client, arguments)
        
        # Verify DOI was formatted correctly
        mock_openalex_client.get_works.assert_called_once_with(
            work_id="https://doi.org/10.48550/arxiv.1706.03762"
        )

    @pytest.mark.asyncio
    async def test_get_work_details_not_found(self, mock_openalex_client):
        """Test work detail retrieval when work not found."""
        mock_openalex_client.get_works = AsyncMock(return_value=None)
        
        arguments = {"work_id": "W999999"}
        
        results = await get_work_details(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Work not found" in results[0].text

    @pytest.mark.asyncio
    async def test_get_author_profile_success(self, mock_openalex_client, sample_author_data):
        """Test successful author profile retrieval."""
        mock_openalex_client.get_authors = AsyncMock(return_value=sample_author_data)
        
        arguments = {"author_id": "A2208157607"}
        
        results = await get_author_profile(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "Ashish Vaswani" in results[0].text
        assert "Recent Publication Activity" in results[0].text

    @pytest.mark.asyncio
    async def test_get_author_profile_orcid_format(self, mock_openalex_client, sample_author_data):
        """Test author profile retrieval with ORCID input."""
        mock_openalex_client.get_authors = AsyncMock(return_value=sample_author_data)
        
        arguments = {"author_id": "0000-0003-4890-3406"}
        
        results = await get_author_profile(mock_openalex_client, arguments)
        
        # Verify ORCID was formatted correctly
        mock_openalex_client.get_authors.assert_called_once_with(
            author_id="https://orcid.org/0000-0003-4890-3406"
        )

    @pytest.mark.asyncio
    async def test_get_citations_success(self, mock_openalex_client, sample_work_data, sample_search_response):
        """Test successful citation retrieval."""
        sample_search_response["results"] = [sample_work_data]
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "work_id": "W2741809807",
            "sort": "cited_by_count",
            "limit": 10
        }
        
        results = await get_citations(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "citing W2741809807" in results[0].text
        
        # Verify filter was applied correctly
        call_args = mock_openalex_client.get_works.call_args
        filter_params = call_args.kwargs["filter_params"]
        assert filter_params["cites"] == "W2741809807"

    @pytest.mark.asyncio
    async def test_get_citations_no_results(self, mock_openalex_client, sample_search_response):
        """Test citation retrieval with no results."""
        sample_search_response["results"] = []
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {"work_id": "W999999"}
        
        results = await get_citations(mock_openalex_client, arguments)
        
        assert len(results) == 1
        assert "No citations found" in results[0].text


class TestToolParameterHandling:
    """Test parameter handling in tools."""

    @pytest.mark.asyncio
    async def test_search_works_default_parameters(self, mock_openalex_client, sample_search_response):
        """Test search works with default parameters."""
        sample_search_response["results"] = []
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        # Only required parameter
        arguments = {"query": "test"}
        
        await search_works(mock_openalex_client, arguments)
        
        call_args = mock_openalex_client.get_works.call_args
        assert call_args.kwargs["sort"] == "relevance_score"  # default
        assert call_args.kwargs["per_page"] == 10  # default limit

    @pytest.mark.asyncio
    async def test_search_works_year_range(self, mock_openalex_client, sample_search_response):
        """Test search works with year range filters."""
        sample_search_response["results"] = []
        mock_openalex_client.get_works = AsyncMock(return_value=sample_search_response)
        
        arguments = {
            "query": "test",
            "year_from": 2020,
            "year_to": 2023
        }
        
        await search_works(mock_openalex_client, arguments)
        
        call_args = mock_openalex_client.get_works.call_args
        filter_params = call_args.kwargs["filter_params"]
        
        # Should use date range filters when both year_from and year_to are provided
        assert "from_publication_date" in filter_params
        assert "to_publication_date" in filter_params
        assert filter_params["from_publication_date"] == "2020-01-01"
        assert filter_params["to_publication_date"] == "2023-12-31"