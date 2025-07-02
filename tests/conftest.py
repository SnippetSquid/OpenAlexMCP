"""Pytest configuration and fixtures."""

import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from src.openalex_mcp.client import OpenAlexClient


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for testing without actual API calls."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    return mock_client


@pytest.fixture
def sample_work_data():
    """Sample OpenAlex work data for testing."""
    return {
        "id": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.48550/arxiv.1706.03762",
        "title": "Attention Is All You Need",
        "display_name": "Attention Is All You Need",
        "publication_year": 2017,
        "publication_date": "2017-06-12",
        "type": "article",
        "type_crossref": "journal-article",
        "authorships": [
            {
                "author_position": "first",
                "author": {
                    "id": "https://openalex.org/A2208157607",
                    "display_name": "Ashish Vaswani",
                    "orcid": "https://orcid.org/0000-0003-4890-3406"
                },
                "institutions": [
                    {
                        "id": "https://openalex.org/I1281959269",
                        "display_name": "Google",
                        "ror": "https://ror.org/006w34k90",
                        "country_code": "US",
                        "type": "company"
                    }
                ],
                "countries": ["US"],
                "is_corresponding": False
            }
        ],
        "primary_location": {
            "source": {
                "id": "https://openalex.org/S4210174132",
                "display_name": "arXiv (Cornell University)",
                "issn_l": None,
                "issn": None,
                "is_oa": True,
                "is_in_doaj": False,
                "type": "repository"
            },
            "landing_page_url": "https://arxiv.org/abs/1706.03762",
            "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
            "is_oa": True,
            "version": "submittedVersion",
            "license": None
        },
        "topics": [
            {
                "id": "https://openalex.org/T11986",
                "display_name": "Machine Learning",
                "score": 0.9999,
                "subfield": {
                    "id": "https://openalex.org/subfields/1702",
                    "display_name": "Artificial Intelligence"
                },
                "field": {
                    "id": "https://openalex.org/fields/17",
                    "display_name": "Computer Science"
                },
                "domain": {
                    "id": "https://openalex.org/domains/3",
                    "display_name": "Physical Sciences"
                }
            }
        ],
        "cited_by_count": 15234,
        "citation_normalized_percentile": 99.9,
        "counts_by_year": [
            {"year": 2023, "cited_by_count": 2500, "works_count": 0},
            {"year": 2022, "cited_by_count": 3200, "works_count": 0}
        ],
        "referenced_works": [],
        "cited_by_api_url": "https://api.openalex.org/works?filter=cites:W2741809807",
        "is_retracted": False,
        "is_paratext": False,
        "language": "en",
        "created_date": "2017-06-15",
        "updated_date": "2023-10-20T00:17:45.648901"
    }


@pytest.fixture
def sample_author_data():
    """Sample OpenAlex author data for testing."""
    return {
        "id": "https://openalex.org/A2208157607",
        "orcid": "https://orcid.org/0000-0003-4890-3406",
        "display_name": "Ashish Vaswani",
        "display_name_alternatives": ["A. Vaswani"],
        "works_count": 45,
        "cited_by_count": 25000,
        "i10_index": 35,
        "h_index": 32,
        "last_known_institution": {
            "id": "https://openalex.org/I1281959269",
            "display_name": "Google",
            "ror": "https://ror.org/006w34k90",
            "country_code": "US",
            "type": "company"
        },
        "affiliations": [
            {
                "institution": {
                    "id": "https://openalex.org/I1281959269",
                    "display_name": "Google"
                },
                "years": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
            }
        ],
        "topics": [
            {
                "id": "https://openalex.org/T11986",
                "display_name": "Machine Learning",
                "score": 95.2
            }
        ],
        "summary_stats": {
            "2yr_mean_citedness": 125.5,
            "h_index": 32,
            "i10_index": 35
        },
        "counts_by_year": [
            {"year": 2023, "works_count": 3, "cited_by_count": 1500},
            {"year": 2022, "works_count": 5, "cited_by_count": 2200}
        ],
        "works_api_url": "https://api.openalex.org/works?filter=author.id:A2208157607",
        "created_date": "2017-08-08",
        "updated_date": "2023-10-20T10:21:34.753320"
    }


@pytest.fixture
def sample_institution_data():
    """Sample OpenAlex institution data for testing."""
    return {
        "id": "https://openalex.org/I205783295",
        "ror": "https://ror.org/00f54p054",
        "display_name": "Stanford University",
        "display_name_alternatives": ["Stanford", "Stanford Univ"],
        "display_name_acronyms": ["SU"],
        "country_code": "US",
        "geo": {
            "city": "Stanford",
            "geonames_city_id": "5398563",
            "region": "California",
            "country_code": "US",
            "country": "United States",
            "latitude": 37.4275,
            "longitude": -122.1697
        },
        "type": "education",
        "homepage_url": "http://www.stanford.edu/",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Seal_of_Leland_Stanford_Junior_University.svg",
        "image_thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Seal_of_Leland_Stanford_Junior_University.svg/100px-Seal_of_Leland_Stanford_Junior_University.svg.png",
        "works_count": 125000,
        "cited_by_count": 15000000,
        "associated_institutions": [],
        "summary_stats": {
            "2yr_mean_citedness": 4.5,
            "h_index": 900,
            "i10_index": 50000
        },
        "counts_by_year": [
            {"year": 2023, "works_count": 8500, "cited_by_count": 750000},
            {"year": 2022, "works_count": 8200, "cited_by_count": 720000}
        ],
        "works_api_url": "https://api.openalex.org/works?filter=institutions.id:I205783295",
        "created_date": "2017-08-08",
        "updated_date": "2023-10-20T10:21:34.753320"
    }


@pytest.fixture
def sample_source_data():
    """Sample OpenAlex source data for testing."""
    return {
        "id": "https://openalex.org/S137773608",
        "issn_l": "0028-0836",
        "issn": ["0028-0836", "1476-4687"],
        "display_name": "Nature",
        "host_organization": "https://openalex.org/P4310320595",
        "host_organization_name": "Springer Nature",
        "host_organization_lineage": ["https://openalex.org/P4310320595"],
        "type": "journal",
        "is_oa": False,
        "is_in_doaj": False,
        "works_count": 500000,
        "cited_by_count": 25000000,
        "h_index": 1200,
        "i10_index": 250000,
        "summary_stats": {
            "2yr_mean_citedness": 12.5,
            "h_index": 1200,
            "i10_index": 250000
        },
        "counts_by_year": [
            {"year": 2023, "works_count": 3500, "cited_by_count": 1250000},
            {"year": 2022, "works_count": 3200, "cited_by_count": 1180000}
        ],
        "homepage_url": "https://www.nature.com/",
        "works_api_url": "https://api.openalex.org/works?filter=primary_location.source.id:S137773608",
        "created_date": "2017-08-08",
        "updated_date": "2023-10-20T10:21:34.753320"
    }


@pytest.fixture
def sample_search_response():
    """Sample OpenAlex search response structure."""
    return {
        "meta": {
            "count": 1234,
            "db_response_time_ms": 45,
            "page": 1,
            "per_page": 25,
            "groups_count": None
        },
        "results": [],  # Will be populated with specific test data
        "group_by": None
    }


@pytest.fixture
def mock_openalex_client():
    """Return a proper AsyncMock for OpenAlexClient for use in async tool tests."""
    return AsyncMock(spec=OpenAlexClient)
