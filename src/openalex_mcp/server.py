"""OpenAlex MCP Server - Main server implementation using FastMCP."""

import os
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP

from openalex_mcp.client import OpenAlexClient
from openalex_mcp.tools import (
    search_works,
    search_authors,
    search_institutions,
    search_sources,
    get_work_details,
    get_author_profile,
    get_citations,
)

# Initialize FastMCP server
mcp = FastMCP("openalex-mcp")

email = os.getenv("OPENALEX_EMAIL")


@mcp.tool()
async def search_works_tool(
    query: str,
    author: str = None,
    year_from: int = None,
    year_to: int = None,
    venue: str = None,
    topic: str = None,
    open_access: bool = None,
    sort: str = "relevance_score",
    limit: int = 10
) -> str:
    """Search for scholarly works (papers, articles, books) in OpenAlex."""
    client = OpenAlexClient(email=email)
    arguments = {
        "query": query,
        "author": author,
        "year_from": year_from,
        "year_to": year_to,
        "venue": venue,
        "topic": topic,
        "open_access": open_access,
        "sort": sort,
        "limit": limit
    }
    # Remove None values
    arguments = {k: v for k, v in arguments.items() if v is not None}
    
    async with client:
        result = await search_works(client, arguments)
        return result[0].text if result else "No results found"


@mcp.tool()
async def search_authors_tool(
    query: str,
    institution: str = None,
    topic: str = None,
    h_index_min: int = None,
    works_count_min: int = None,
    sort: str = "relevance_score",
    limit: int = 10
) -> str:
    """Search for authors/researchers in OpenAlex."""
    client = OpenAlexClient(email=email)
    arguments = {
        "query": query,
        "institution": institution,
        "topic": topic,
        "h_index_min": h_index_min,
        "works_count_min": works_count_min,
        "sort": sort,
        "limit": limit
    }
    # Remove None values
    arguments = {k: v for k, v in arguments.items() if v is not None}
    
    async with client:
        result = await search_authors(client, arguments)
        return result[0].text if result else "No results found"


@mcp.tool()
async def search_institutions_tool(
    query: str,
    country: str = None,
    institution_type: str = None,
    works_count_min: int = None,
    sort: str = "relevance_score",
    limit: int = 10
) -> str:
    """Search for academic institutions in OpenAlex."""
    client = OpenAlexClient(email=email)
    arguments = {
        "query": query,
        "country": country,
        "type": institution_type,
        "works_count_min": works_count_min,
        "sort": sort,
        "limit": limit
    }
    # Remove None values
    arguments = {k: v for k, v in arguments.items() if v is not None}
    
    async with client:
        result = await search_institutions(client, arguments)
        return result[0].text if result else "No results found"


@mcp.tool()
async def search_sources_tool(
    query: str,
    source_type: str = None,
    publisher: str = None,
    open_access: bool = None,
    works_count_min: int = None,
    sort: str = "relevance_score",
    limit: int = 10
) -> str:
    """Search for journals, conferences, and other publication venues in OpenAlex."""
    client = OpenAlexClient(email=email)
    arguments = {
        "query": query,
        "type": source_type,
        "publisher": publisher,
        "open_access": open_access,
        "works_count_min": works_count_min,
        "sort": sort,
        "limit": limit
    }
    # Remove None values
    arguments = {k: v for k, v in arguments.items() if v is not None}
    
    async with client:
        result = await search_sources(client, arguments)
        return result[0].text if result else "No results found"


@mcp.tool()
async def get_work_details_tool(work_id: str) -> str:
    """Get detailed information about a specific work by its OpenAlex ID or DOI."""
    client = OpenAlexClient(email=email)
    arguments = {"work_id": work_id}
    
    async with client:
        result = await get_work_details(client, arguments)
        return result[0].text if result else "Work not found"


@mcp.tool()
async def get_author_profile_tool(author_id: str) -> str:
    """Get detailed profile information about a specific author by their OpenAlex ID or ORCID."""
    client = OpenAlexClient(email=email)
    arguments = {"author_id": author_id}
    
    async with client:
        result = await get_author_profile(client, arguments)
        return result[0].text if result else "Author not found"


@mcp.tool()
async def get_citations_tool(
    work_id: str,
    sort: str = "publication_date",
    limit: int = 20
) -> str:
    """Get works that cite a specific work, useful for citation analysis."""
    client = OpenAlexClient(email=email)
    arguments = {
        "work_id": work_id,
        "sort": sort,
        "limit": limit
    }
    
    async with client:
        result = await get_citations(client, arguments)
        return result[0].text if result else "No citations found"


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()