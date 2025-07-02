"""MCP tools for OpenAlex API interactions."""

import os
import re
from typing import Any, Dict, List

from mcp.types import TextContent, Tool

from openalex_mcp.client import OpenAlexClient


def format_work_summary(work: Dict[str, Any]) -> str:
    """Format a work into a readable summary."""
    title = work.get("title") or work.get("display_name", "Unknown Title")
    authors = []

    for authorship in work.get("authorships", []):
        if author := authorship.get("author"):
            if name := author.get("display_name"):
                authors.append(name)

    authors_str = ", ".join(authors[:5])  # Limit to first 5 authors
    if len(work.get("authorships", [])) > 5:
        authors_str += " et al."

    year = work.get("publication_year", "Unknown")
    citations = work.get("cited_by_count", 0)

    # Get venue/source
    venue = "Unknown Venue"
    if primary_location := work.get("primary_location"):
        if source := primary_location.get("source"):
            venue = source.get("display_name", venue)

    # Get topics
    topics = []
    for topic in work.get("topics", [])[:3]:  # First 3 topics
        if topic_name := topic.get("display_name"):
            topics.append(topic_name)

    topics_str = ", ".join(topics) if topics else "No topics"

    return (
        f"**{title}**\n"
        f"Authors: {authors_str}\n"
        f"Year: {year} | Citations: {citations}\n"
        f"Venue: {venue}\n"
        f"Topics: {topics_str}\n"
        f"OpenAlex ID: {work.get('id', 'N/A')}\n"
    )


def format_author_summary(author: Dict[str, Any]) -> str:
    """Format an author into a readable summary."""
    name = author.get("display_name", "Unknown Author")
    orcid = author.get("orcid", "No ORCID")
    works_count = author.get("works_count", 0)
    citations = author.get("cited_by_count", 0)
    h_index = author.get("h_index", 0)

    # Institution
    institution = "Unknown Institution"
    if last_inst := author.get("last_known_institution"):
        institution = last_inst.get("display_name", institution)

    # Topics
    topics = []
    for topic in author.get("topics", [])[:3]:  # First 3 topics
        if topic_name := topic.get("display_name"):
            topics.append(topic_name)

    topics_str = ", ".join(topics) if topics else "No topics"

    return (
        f"**{name}**\n"
        f"ORCID: {orcid}\n"
        f"Institution: {institution}\n"
        f"Works: {works_count} | Citations: {citations} | h-index: {h_index}\n"
        f"Research areas: {topics_str}\n"
        f"OpenAlex ID: {author.get('id', 'N/A')}\n"
    )


def format_institution_summary(institution: Dict[str, Any]) -> str:
    """Format an institution into a readable summary."""
    name = institution.get("display_name", "Unknown Institution")
    country = institution.get("country_code", "Unknown")
    inst_type = institution.get("type", "Unknown Type")
    works_count = institution.get("works_count", 0)
    citations = institution.get("cited_by_count", 0)
    ror = institution.get("ror", "No ROR")
    homepage = institution.get("homepage_url", "No homepage")

    return (
        f"**{name}**\n"
        f"Type: {inst_type} | Country: {country}\n"
        f"Works: {works_count} | Citations: {citations}\n"
        f"ROR: {ror}\n"
        f"Homepage: {homepage}\n"
        f"OpenAlex ID: {institution.get('id', 'N/A')}\n"
    )


def format_source_summary(source: Dict[str, Any]) -> str:
    """Format a source into a readable summary."""
    name = source.get("display_name", "Unknown Source")
    source_type = source.get("type", "Unknown Type")
    issn = source.get("issn_l", "No ISSN")
    is_oa = source.get("is_oa", False)
    works_count = source.get("works_count", 0)
    citations = source.get("cited_by_count", 0)
    h_index = source.get("h_index", 0)

    # Publisher
    publisher = "Unknown Publisher"
    if host_org := source.get("host_organization_name"):
        publisher = host_org

    return (
        f"**{name}**\n"
        f"Type: {source_type} | Publisher: {publisher}\n"
        f"ISSN-L: {issn} | Open Access: {'Yes' if is_oa else 'No'}\n"
        f"Works: {works_count} | Citations: {citations} | h-index: {h_index}\n"
        f"OpenAlex ID: {source.get('id', 'N/A')}\n"
    )


# Tool definitions
SEARCH_WORKS_TOOL = Tool(
    name="search_works",
    description="Search for scholarly works (papers, articles, books) in OpenAlex",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for works (title, abstract, keywords)"
            },
            "author": {
                "type": "string",
                "description": "Filter by author name"
            },
            "year_from": {
                "type": "integer",
                "description": "Filter works from this year onwards"
            },
            "year_to": {
                "type": "integer",
                "description": "Filter works up to this year"
            },
            "venue": {
                "type": "string",
                "description": "Filter by venue/journal name"
            },
            "topic": {
                "type": "string",
                "description": "Filter by research topic/field"
            },
            "open_access": {
                "type": "boolean",
                "description": "Filter for open access works only"
            },
            "sort": {
                "type": "string",
                "enum": ["cited_by_count", "publication_date"],
                "description": "Sort order for results (default: relevance)"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 10,
                "description": "Number of results to return (max 50)"
            }
        },
        "required": ["query"]
    }
)

SEARCH_AUTHORS_TOOL = Tool(
    name="search_authors",
    description="Search for authors/researchers in OpenAlex",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for author names"
            },
            "institution": {
                "type": "string",
                "description": "Filter by institution name"
            },
            "topic": {
                "type": "string",
                "description": "Filter by research area/topic"
            },
            "h_index_min": {
                "type": "integer",
                "description": "Minimum h-index"
            },
            "works_count_min": {
                "type": "integer",
                "description": "Minimum number of works"
            },
            "sort": {
                "type": "string",
                "enum": ["relevance_score", "cited_by_count", "works_count", "h_index"],
                "description": "Sort order for results"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 10,
                "description": "Number of results to return (max 50)"
            }
        },
        "required": ["query"]
    }
)

SEARCH_INSTITUTIONS_TOOL = Tool(
    name="search_institutions",
    description="Search for academic institutions in OpenAlex",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for institution names"
            },
            "country": {
                "type": "string",
                "description": "Filter by country code (e.g., 'US', 'GB', 'CA')"
            },
            "type": {
                "type": "string",
                "enum": ["education", "healthcare", "company", "archive", "nonprofit", "government", "facility", "other"],
                "description": "Filter by institution type"
            },
            "works_count_min": {
                "type": "integer",
                "description": "Minimum number of works"
            },
            "sort": {
                "type": "string",
                "enum": ["relevance_score", "cited_by_count", "works_count"],
                "description": "Sort order for results"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 10,
                "description": "Number of results to return (max 50)"
            }
        },
        "required": ["query"]
    }
)

SEARCH_SOURCES_TOOL = Tool(
    name="search_sources",
    description="Search for journals, conferences, and other publication venues in OpenAlex",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for source names"
            },
            "type": {
                "type": "string",
                "enum": ["journal", "conference", "repository", "book-series", "other"],
                "description": "Filter by source type"
            },
            "publisher": {
                "type": "string",
                "description": "Filter by publisher name"
            },
            "open_access": {
                "type": "boolean",
                "description": "Filter for open access sources only"
            },
            "works_count_min": {
                "type": "integer",
                "description": "Minimum number of works published"
            },
            "sort": {
                "type": "string",
                "enum": ["relevance_score", "cited_by_count", "works_count", "h_index"],
                "description": "Sort order for results"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 10,
                "description": "Number of results to return (max 50)"
            }
        },
        "required": ["query"]
    }
)

GET_WORK_DETAILS_TOOL = Tool(
    name="get_work_details",
    description="Get detailed information about a specific work by its OpenAlex ID or DOI",
    inputSchema={
        "type": "object",
        "properties": {
            "work_id": {
                "type": "string",
                "description": "OpenAlex work ID (e.g., 'W2741809807') or DOI"
            }
        },
        "required": ["work_id"]
    }
)

GET_AUTHOR_PROFILE_TOOL = Tool(
    name="get_author_profile",
    description="Get detailed profile information about a specific author by their OpenAlex ID or ORCID",
    inputSchema={
        "type": "object",
        "properties": {
            "author_id": {
                "type": "string",
                "description": "OpenAlex author ID (e.g., 'A5023888391') or ORCID"
            }
        },
        "required": ["author_id"]
    }
)

GET_CITATIONS_TOOL = Tool(
    name="get_citations",
    description="Get works that cite a specific work, useful for citation analysis",
    inputSchema={
        "type": "object",
        "properties": {
            "work_id": {
                "type": "string",
                "description": "OpenAlex work ID or DOI of the work to find citations for"
            },
            "sort": {
                "type": "string",
                "enum": ["publication_date", "cited_by_count", "relevance_score"],
                "description": "Sort order for citing works"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 20,
                "description": "Number of citing works to return (max 50)"
            }
        },
        "required": ["work_id"]
    }
)

DOWNLOAD_PAPER_TOOL = Tool(
    name="download_paper",
    description="Download a paper's PDF if available through open access",
    inputSchema={
        "type": "object",
        "properties": {
            "work_id": {
                "type": "string",
                "description": "OpenAlex work ID (e.g., 'W2741809807') or DOI of the work to download"
            },
            "output_path": {
                "type": "string",
                "description": "Directory path where to save the PDF file (optional, defaults to current directory)"
            },
            "filename": {
                "type": "string",
                "description": "Custom filename for the PDF (optional, auto-generated if not provided)"
            }
        },
        "required": ["work_id"]
    }
)


async def search_works(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for works in OpenAlex."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    sort = arguments.get("sort")  # No default sort - let OpenAlex use relevance

    # Build filter parameters
    filter_params = {}

    if author := arguments.get("author"):
        filter_params["raw_author_name.search"] = author

    # Handle year range properly using separate filters
    year_from = arguments.get("year_from")
    year_to = arguments.get("year_to")

    # Ensure year values are integers
    if year_from is not None:
        year_from = int(year_from)
    if year_to is not None:
        year_to = int(year_to)

    if year_from and year_to:
        # Use date range filters for both
        filter_params["from_publication_date"] = f"{year_from}-01-01"
        filter_params["to_publication_date"] = f"{year_to}-12-31"
    elif year_from:
        filter_params["publication_year"] = f">={year_from}"
    elif year_to:
        filter_params["publication_year"] = f"<={year_to}"

    if venue := arguments.get("venue"):
        filter_params["primary_location.source.display_name.search"] = venue

    if topic := arguments.get("topic"):
        filter_params["topics.display_name.search"] = topic

    if arguments.get("open_access"):
        filter_params["is_oa"] = "true"

    try:
        response = await client.get_works(
            search=query,
            filter_params=filter_params,
            sort=sort,
            per_page=limit
        )

        results = response.get("results", [])
        meta = response.get("meta", {})

        if not results:
            return [TextContent(
                type="text",
                text=f"No works found for query: '{query}'"
            )]

        # Format results
        content = f"Found {meta.get('count', len(results))} works for '{query}':\n\n"

        for i, work in enumerate(results, 1):
            content += f"{i}. {format_work_summary(work)}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching works: {str(e)}"
        )]


async def search_authors(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for authors in OpenAlex."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    sort = arguments.get("sort", "cited_by_count")

    # Build filter parameters
    filter_params = {}

    if institution := arguments.get("institution"):
        filter_params["last_known_institution.display_name.search"] = institution

    if topic := arguments.get("topic"):
        filter_params["topics.display_name.search"] = topic

    if h_index_min := arguments.get("h_index_min"):
        filter_params["h_index"] = f">={h_index_min}"

    if works_count_min := arguments.get("works_count_min"):
        filter_params["works_count"] = f">={works_count_min}"

    try:
        response = await client.get_authors(
            search=query,
            filter_params=filter_params,
            sort=sort,
            per_page=limit
        )

        results = response.get("results", [])
        meta = response.get("meta", {})

        if not results:
            return [TextContent(
                type="text",
                text=f"No authors found for query: '{query}'"
            )]

        # Format results
        content = f"Found {meta.get('count', len(results))} authors for '{query}':\n\n"

        for i, author in enumerate(results, 1):
            content += f"{i}. {format_author_summary(author)}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching authors: {str(e)}"
        )]


async def search_institutions(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for institutions in OpenAlex."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    sort = arguments.get("sort", "cited_by_count")

    # Build filter parameters
    filter_params = {}

    if country := arguments.get("country"):
        filter_params["country_code"] = country

    if inst_type := arguments.get("type"):
        filter_params["type"] = inst_type

    if works_count_min := arguments.get("works_count_min"):
        filter_params["works_count"] = f">={works_count_min}"

    try:
        response = await client.get_institutions(
            search=query,
            filter_params=filter_params,
            sort=sort,
            per_page=limit
        )

        results = response.get("results", [])
        meta = response.get("meta", {})

        if not results:
            return [TextContent(
                type="text",
                text=f"No institutions found for query: '{query}'"
            )]

        # Format results
        content = f"Found {meta.get('count', len(results))} institutions for '{query}':\n\n"

        for i, institution in enumerate(results, 1):
            content += f"{i}. {format_institution_summary(institution)}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching institutions: {str(e)}"
        )]


async def search_sources(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for sources in OpenAlex."""
    query = arguments["query"]
    limit = arguments.get("limit", 10)
    sort = arguments.get("sort", "cited_by_count")

    # Build filter parameters
    filter_params = {}

    if source_type := arguments.get("type"):
        filter_params["type"] = source_type

    if publisher := arguments.get("publisher"):
        filter_params["host_organization_name.search"] = publisher

    if arguments.get("open_access"):
        filter_params["is_oa"] = "true"

    if works_count_min := arguments.get("works_count_min"):
        filter_params["works_count"] = f">={works_count_min}"

    try:
        response = await client.get_sources(
            search=query,
            filter_params=filter_params,
            sort=sort,
            per_page=limit
        )

        results = response.get("results", [])
        meta = response.get("meta", {})

        if not results:
            return [TextContent(
                type="text",
                text=f"No sources found for query: '{query}'"
            )]

        # Format results
        content = f"Found {meta.get('count', len(results))} sources for '{query}':\n\n"

        for i, source in enumerate(results, 1):
            content += f"{i}. {format_source_summary(source)}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching sources: {str(e)}"
        )]


async def get_work_details(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Get detailed information about a specific work."""
    work_id = arguments["work_id"]

    # Handle DOI format
    if work_id.startswith("10."):
        work_id = f"https://doi.org/{work_id}"
    elif not work_id.startswith(("W", "https://openalex.org/W", "https://doi.org/")):
        work_id = f"W{work_id}"

    try:
        response = await client.get_works(work_id=work_id)

        if not response:
            return [TextContent(
                type="text",
                text=f"Work not found: {work_id}"
            )]

        work = response

        # Format detailed work information
        content = format_work_summary(work)

        # Add additional details
        if doi := work.get("doi"):
            content += f"DOI: {doi}\n"

        if abstract := work.get("abstract_inverted_index"):
            # Convert inverted index to abstract (simplified)
            content += "Has abstract: Yes\n"
        else:
            content += "Has abstract: No\n"

        if work.get("is_oa"):
            content += "Open Access: Yes\n"
            if best_oa := work.get("best_oa_location"):
                if pdf_url := best_oa.get("pdf_url"):
                    content += f"PDF URL: {pdf_url}\n"

        # Add reference count
        ref_count = len(work.get("referenced_works", []))
        content += f"References: {ref_count} works\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting work details: {str(e)}"
        )]


async def get_author_profile(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Get detailed profile information about a specific author."""
    author_id = arguments["author_id"]

    # Handle ORCID format
    if author_id.startswith("0000-"):
        author_id = f"https://orcid.org/{author_id}"
    elif not author_id.startswith(("A", "https://openalex.org/A", "https://orcid.org/")):
        author_id = f"A{author_id}"

    try:
        response = await client.get_authors(author_id=author_id)

        if not response:
            return [TextContent(
                type="text",
                text=f"Author not found: {author_id}"
            )]

        author = response

        # Format detailed author information
        content = format_author_summary(author)

        # Add career timeline
        if counts_by_year := author.get("counts_by_year", []):
            recent_years = sorted(counts_by_year, key=lambda x: x.get("year", 0), reverse=True)[:5]
            content += "\n**Recent Publication Activity:**\n"
            for year_data in recent_years:
                year = year_data.get("year")
                works = year_data.get("works_count", 0)
                citations = year_data.get("cited_by_count", 0)
                content += f"- {year}: {works} works, {citations} citations\n"

        # Add alternative names
        if alt_names := author.get("display_name_alternatives", []):
            content += f"\n**Alternative names:** {', '.join(alt_names[:3])}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting author profile: {str(e)}"
        )]


async def get_citations(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Get works that cite a specific work."""
    work_id = arguments["work_id"]
    limit = arguments.get("limit", 20)
    sort = arguments.get("sort", "publication_date")

    # Handle DOI format
    if work_id.startswith("10."):
        work_id = f"https://doi.org/{work_id}"
    elif not work_id.startswith(("W", "https://openalex.org/W", "https://doi.org/")):
        work_id = f"W{work_id}"

    try:
        # Search for works that cite this work
        filter_params = {"cites": work_id}

        response = await client.get_works(
            filter_params=filter_params,
            sort=sort,
            per_page=limit
        )

        results = response.get("results", [])
        meta = response.get("meta", {})

        if not results:
            return [TextContent(
                type="text",
                text=f"No citations found for work: {work_id}"
            )]

        # Format results
        content = f"Found {meta.get('count', len(results))} works citing {work_id}:\n\n"

        for i, work in enumerate(results, 1):
            content += f"{i}. {format_work_summary(work)}\n"

        return [TextContent(type="text", text=content)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting citations: {str(e)}"
        )]


async def download_paper(client: OpenAlexClient, arguments: Dict[str, Any]) -> List[TextContent]:
    """Download a paper's PDF if available through open access."""
    work_id = arguments["work_id"]
    output_path = arguments.get("output_path", ".")
    custom_filename = arguments.get("filename")

    # Handle DOI format
    if work_id.startswith("10."):
        work_id = f"https://doi.org/{work_id}"
    elif not work_id.startswith(("W", "https://openalex.org/W", "https://doi.org/")):
        work_id = f"W{work_id}"

    try:
        # First get the work details to find PDF URL
        response = await client.get_works(work_id=work_id)

        if not response:
            return [TextContent(
                type="text",
                text=f"Work not found: {work_id}"
            )]

        work = response
        title = work.get("title") or work.get("display_name", "Unknown Title")

        # Check if paper has open access PDF
        pdf_url = None
        if work.get("is_oa") and (best_oa := work.get("best_oa_location")):
            pdf_url = best_oa.get("pdf_url")

        if not pdf_url:
            # Check other locations for PDF
            for location in work.get("locations", []):
                if location.get("is_oa") and location.get("pdf_url"):
                    pdf_url = location["pdf_url"]
                    break

        if not pdf_url:
            return [TextContent(
                type="text",
                text=f"No open access PDF available for: {title}\n"
                     f"This paper may be behind a paywall or not available in PDF format."
            )]

        # Generate filename if not provided
        if not custom_filename:
            # Clean title for filename
            clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
            clean_title = clean_title.replace(' ', '_')[:50]  # Limit length
            custom_filename = f"{clean_title}.pdf"

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Full file path
        file_path = os.path.join(output_path, custom_filename)

        # Download the PDF
        success = await client.download_pdf(pdf_url, file_path)

        if success:
            # Get file size for confirmation
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            return [TextContent(
                type="text",
                text=f"Successfully downloaded: {title}\n"
                     f"File: {file_path}\n"
                     f"Size: {file_size_mb:.2f} MB\n"
                     f"Source: {pdf_url}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to download PDF for: {title}\n"
                     f"URL: {pdf_url}\n"
                     f"Check logs for detailed error information."
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error downloading paper: {str(e)}"
        )]
