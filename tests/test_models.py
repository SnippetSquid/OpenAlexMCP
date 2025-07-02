"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from src.openalex_mcp.models import (
    Author,
    AuthorInfo,
    Institution,
    InstitutionModel,
    SearchResponse,
    SourceModel,
    Topic,
    TopicModel,
    Work,
)


class TestBasicModels:
    """Test basic model components."""

    def test_author_info_creation(self):
        """Test AuthorInfo model creation."""
        author_info = AuthorInfo(
            id="https://openalex.org/A123",
            display_name="John Doe",
            orcid="https://orcid.org/0000-0000-0000-0000"
        )

        assert author_info.id == "https://openalex.org/A123"
        assert author_info.display_name == "John Doe"
        assert author_info.orcid == "https://orcid.org/0000-0000-0000-0000"

    def test_author_info_optional_fields(self):
        """Test AuthorInfo with optional fields."""
        author_info = AuthorInfo()

        assert author_info.id is None
        assert author_info.display_name is None
        assert author_info.orcid is None

    def test_institution_creation(self):
        """Test Institution model creation."""
        institution = Institution(
            id="https://openalex.org/I123",
            display_name="Test University",
            ror="https://ror.org/12345",
            country_code="US",
            type="education"
        )

        assert institution.id == "https://openalex.org/I123"
        assert institution.display_name == "Test University"
        assert institution.country_code == "US"

    def test_topic_creation(self):
        """Test Topic model creation."""
        topic = Topic(
            id="https://openalex.org/T123",
            display_name="Machine Learning",
            score=0.95
        )

        assert topic.id == "https://openalex.org/T123"
        assert topic.display_name == "Machine Learning"
        assert topic.score == 0.95


class TestWorkModel:
    """Test the Work model."""

    def test_work_creation_minimal(self):
        """Test Work creation with minimal required fields."""
        work = Work(id="https://openalex.org/W123")

        assert work.id == "https://openalex.org/W123"
        assert work.doi is None
        assert work.title is None
        assert work.authorships == []
        assert work.topics == []

    def test_work_creation_full(self, sample_work_data):
        """Test Work creation with full data."""
        work = Work(**sample_work_data)

        assert work.id == sample_work_data["id"]
        assert work.title == sample_work_data["title"]
        assert work.publication_year == sample_work_data["publication_year"]
        assert work.cited_by_count == sample_work_data["cited_by_count"]
        assert len(work.authorships) == len(sample_work_data["authorships"])
        assert len(work.topics) == len(sample_work_data["topics"])

    def test_work_authorship_nested(self, sample_work_data):
        """Test Work with nested authorship data."""
        work = Work(**sample_work_data)

        authorship = work.authorships[0]
        assert authorship.author_position == "first"
        assert authorship.author.display_name == "Ashish Vaswani"
        assert len(authorship.institutions) == 1
        assert authorship.institutions[0].display_name == "Google"

    def test_work_primary_location(self, sample_work_data):
        """Test Work with primary location data."""
        work = Work(**sample_work_data)

        assert work.primary_location is not None
        assert work.primary_location.source.display_name == "arXiv (Cornell University)"
        assert work.primary_location.is_oa is True

    def test_work_invalid_id(self):
        """Test Work creation with invalid ID type."""
        with pytest.raises(ValidationError):
            Work(id=123)  # ID should be string


class TestAuthorModel:
    """Test the Author model."""

    def test_author_creation_minimal(self):
        """Test Author creation with minimal required fields."""
        author = Author(id="https://openalex.org/A123")

        assert author.id == "https://openalex.org/A123"
        assert author.display_name is None
        assert author.works_count is None
        assert author.affiliations == []

    def test_author_creation_full(self, sample_author_data):
        """Test Author creation with full data."""
        author = Author(**sample_author_data)

        assert author.id == sample_author_data["id"]
        assert author.display_name == sample_author_data["display_name"]
        assert author.works_count == sample_author_data["works_count"]
        assert author.h_index == sample_author_data["h_index"]
        assert len(author.display_name_alternatives) == 1

    def test_author_institution_relationship(self, sample_author_data):
        """Test Author with institution relationship."""
        author = Author(**sample_author_data)

        assert author.last_known_institution is not None
        assert author.last_known_institution.display_name == "Google"
        assert len(author.affiliations) == 1


class TestInstitutionModel:
    """Test the InstitutionModel."""

    def test_institution_creation_minimal(self):
        """Test Institution creation with minimal required fields."""
        institution = InstitutionModel(id="https://openalex.org/I123")

        assert institution.id == "https://openalex.org/I123"
        assert institution.display_name is None
        assert institution.works_count is None

    def test_institution_creation_full(self, sample_institution_data):
        """Test Institution creation with full data."""
        institution = InstitutionModel(**sample_institution_data)

        assert institution.id == sample_institution_data["id"]
        assert institution.display_name == sample_institution_data["display_name"]
        assert institution.country_code == sample_institution_data["country_code"]
        assert institution.works_count == sample_institution_data["works_count"]


class TestSourceModel:
    """Test the SourceModel."""

    def test_source_creation_minimal(self):
        """Test Source creation with minimal required fields."""
        source = SourceModel(id="https://openalex.org/S123")

        assert source.id == "https://openalex.org/S123"
        assert source.display_name is None
        assert source.issn is None

    def test_source_creation_full(self, sample_source_data):
        """Test Source creation with full data."""
        source = SourceModel(**sample_source_data)

        assert source.id == sample_source_data["id"]
        assert source.display_name == sample_source_data["display_name"]
        assert source.issn_l == sample_source_data["issn_l"]
        assert source.is_oa == sample_source_data["is_oa"]


class TestTopicModel:
    """Test the TopicModel."""

    def test_topic_creation_minimal(self):
        """Test Topic creation with minimal required fields."""
        topic = TopicModel(id="https://openalex.org/T123")

        assert topic.id == "https://openalex.org/T123"
        assert topic.display_name is None
        assert topic.keywords == []

    def test_topic_creation_with_hierarchy(self):
        """Test Topic creation with hierarchical data."""
        topic_data = {
            "id": "https://openalex.org/T123",
            "display_name": "Machine Learning",
            "subfield": {"id": "SF123", "display_name": "AI"},
            "field": {"id": "F123", "display_name": "Computer Science"},
            "domain": {"id": "D123", "display_name": "Physical Sciences"}
        }

        topic = TopicModel(**topic_data)

        assert topic.subfield["display_name"] == "AI"
        assert topic.field["display_name"] == "Computer Science"
        assert topic.domain["display_name"] == "Physical Sciences"


class TestSearchResponse:
    """Test the SearchResponse model."""

    def test_search_response_creation(self):
        """Test SearchResponse creation."""
        response_data = {
            "meta": {
                "count": 100,
                "page": 1,
                "per_page": 25
            },
            "results": [
                {"id": "W123", "title": "Test Work"},
                {"id": "W456", "title": "Another Work"}
            ]
        }

        response = SearchResponse(**response_data)

        assert response.meta["count"] == 100
        assert len(response.results) == 2
        assert response.group_by is None

    def test_search_response_with_groupby(self):
        """Test SearchResponse with group_by data."""
        response_data = {
            "meta": {"count": 50},
            "results": [],
            "group_by": [
                {"key": "2023", "count": 25},
                {"key": "2022", "count": 25}
            ]
        }

        response = SearchResponse(**response_data)

        assert len(response.group_by) == 2
        assert response.group_by[0]["key"] == "2023"


class TestModelValidation:
    """Test model validation and error handling."""

    def test_work_missing_id(self):
        """Test Work creation without required ID."""
        with pytest.raises(ValidationError) as exc_info:
            Work()

        assert "id" in str(exc_info.value)

    def test_author_missing_id(self):
        """Test Author creation without required ID."""
        with pytest.raises(ValidationError) as exc_info:
            Author()

        assert "id" in str(exc_info.value)

    def test_work_invalid_year(self):
        """Test Work with invalid publication year."""
        with pytest.raises(ValidationError):
            Work(
                id="W123",
                publication_year="invalid"  # Should be int
            )
        # Pydantic should convert string to int if possible
        # This specific case might pass depending on the string content

    def test_search_response_invalid_structure(self):
        """Test SearchResponse with invalid structure."""
        with pytest.raises(ValidationError):
            SearchResponse(
                meta="invalid",  # Should be dict
                results=[]
            )


class TestModelDefaults:
    """Test model default values."""

    def test_work_list_defaults(self):
        """Test Work model list field defaults."""
        work = Work(id="W123")

        assert work.authorships == []
        assert work.locations == []
        assert work.topics == []
        assert work.keywords == []
        assert work.referenced_works == []
        assert work.counts_by_year == []

    def test_author_list_defaults(self):
        """Test Author model list field defaults."""
        author = Author(id="A123")

        assert author.display_name_alternatives == []
        assert author.affiliations == []
        assert author.topics == []
        assert author.counts_by_year == []

    def test_institution_list_defaults(self):
        """Test Institution model list field defaults."""
        institution = InstitutionModel(id="I123")

        assert institution.display_name_alternatives == []
        assert institution.display_name_acronyms == []
        assert institution.associated_institutions == []
        assert institution.counts_by_year == []
