"""Tests for configuration management."""

from unittest.mock import patch

import pytest

from src.openalex_mcp.config import OpenAlexConfig


class TestOpenAlexConfig:
    """Test the configuration class."""

    @patch.dict('os.environ', {}, clear=True)
    def test_config_default_values(self):
        """Test configuration with default values."""
        config = OpenAlexConfig()

        assert config.email is None
        assert config.timeout == 30.0
        assert config.max_concurrent_requests == 10
        assert config.default_page_size == 25
        assert config.max_page_size == 200
        assert config.daily_request_limit == 100000
        assert config.log_level == "INFO"
        assert config.log_api_requests is False

    @patch.dict('os.environ', {
        'OPENALEX_EMAIL': 'test@example.com',
        'OPENALEX_TIMEOUT': '60.0',
        'OPENALEX_MAX_CONCURRENT': '20',
        'OPENALEX_DEFAULT_PAGE_SIZE': '50',
        'OPENALEX_MAX_PAGE_SIZE': '100',
        'OPENALEX_DAILY_LIMIT': '50000',
        'LOG_LEVEL': 'DEBUG',
        'LOG_API_REQUESTS': 'true'
    })
    def test_config_from_environment(self):
        """Test configuration from environment variables."""
        config = OpenAlexConfig()

        assert config.email == "test@example.com"
        assert config.timeout == 60.0
        assert config.max_concurrent_requests == 20
        assert config.default_page_size == 50
        assert config.max_page_size == 100
        assert config.daily_request_limit == 50000
        assert config.log_level == "DEBUG"
        assert config.log_api_requests is True

    @patch.dict('os.environ', {'LOG_API_REQUESTS': 'false'})
    def test_config_log_api_requests_false(self):
        """Test log_api_requests with 'false' value."""
        config = OpenAlexConfig()
        assert config.log_api_requests is False

    @patch.dict('os.environ', {'LOG_API_REQUESTS': 'TRUE'})
    def test_config_log_api_requests_case_insensitive(self):
        """Test log_api_requests is case insensitive."""
        config = OpenAlexConfig()
        assert config.log_api_requests is True

    def test_validate_success(self):
        """Test successful configuration validation."""
        config = OpenAlexConfig()
        # Should not raise any exception
        config.validate()

    def test_validate_negative_timeout(self):
        """Test validation with negative timeout."""
        config = OpenAlexConfig()
        config.timeout = -1.0

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_TIMEOUT must be positive" in str(exc_info.value)

    def test_validate_zero_timeout(self):
        """Test validation with zero timeout."""
        config = OpenAlexConfig()
        config.timeout = 0.0

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_TIMEOUT must be positive" in str(exc_info.value)

    def test_validate_negative_concurrent_requests(self):
        """Test validation with negative concurrent requests."""
        config = OpenAlexConfig()
        config.max_concurrent_requests = -1

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_MAX_CONCURRENT must be positive" in str(exc_info.value)

    def test_validate_zero_concurrent_requests(self):
        """Test validation with zero concurrent requests."""
        config = OpenAlexConfig()
        config.max_concurrent_requests = 0

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_MAX_CONCURRENT must be positive" in str(exc_info.value)

    def test_validate_zero_default_page_size(self):
        """Test validation with zero default page size."""
        config = OpenAlexConfig()
        config.default_page_size = 0

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_DEFAULT_PAGE_SIZE must be between 1 and" in str(exc_info.value)

    def test_validate_page_size_exceeds_max(self):
        """Test validation with default page size exceeding max."""
        config = OpenAlexConfig()
        config.default_page_size = 300
        config.max_page_size = 200

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_DEFAULT_PAGE_SIZE must be between 1 and 200" in str(exc_info.value)

    def test_validate_negative_daily_limit(self):
        """Test validation with negative daily limit."""
        config = OpenAlexConfig()
        config.daily_request_limit = -1

        with pytest.raises(ValueError) as exc_info:
            config.validate()

        assert "OPENALEX_DAILY_LIMIT must be positive" in str(exc_info.value)

    def test_get_user_agent_without_email(self):
        """Test user agent without email."""
        config = OpenAlexConfig()
        config.email = None

        user_agent = config.get_user_agent()
        assert user_agent == "OpenAlexMCP/0.1.0"

    def test_get_user_agent_with_email(self):
        """Test user agent with email."""
        config = OpenAlexConfig()
        config.email = "test@example.com"

        user_agent = config.get_user_agent()
        assert user_agent == "OpenAlexMCP/0.1.0 (mailto:test@example.com)"

    def test_should_use_polite_pool_without_email(self):
        """Test polite pool check without email."""
        config = OpenAlexConfig()
        config.email = None

        assert config.should_use_polite_pool() is False

    def test_should_use_polite_pool_with_email(self):
        """Test polite pool check with email."""
        config = OpenAlexConfig()
        config.email = "test@example.com"

        assert config.should_use_polite_pool() is True

    def test_should_use_polite_pool_with_empty_email(self):
        """Test polite pool check with empty email."""
        config = OpenAlexConfig()
        config.email = ""

        assert config.should_use_polite_pool() is False


class TestGlobalConfig:
    """Test the global config instance."""

    def test_global_config_exists(self):
        """Test that global config instance exists."""
        from src.openalex_mcp.config import config

        assert config is not None
        assert isinstance(config, OpenAlexConfig)

    def test_global_config_validation(self):
        """Test that global config is valid."""
        from src.openalex_mcp.config import config

        # Should not raise any exception
        config.validate()


class TestConfigEnvironmentVariableParsing:
    """Test parsing of different environment variable types."""

    @patch.dict('os.environ', {'OPENALEX_TIMEOUT': 'invalid'})
    def test_invalid_float_environment_variable(self):
        """Test handling of invalid float environment variable."""
        with pytest.raises(ValueError):
            OpenAlexConfig()

    @patch.dict('os.environ', {'OPENALEX_MAX_CONCURRENT': 'invalid'})
    def test_invalid_int_environment_variable(self):
        """Test handling of invalid integer environment variable."""
        with pytest.raises(ValueError):
            OpenAlexConfig()

    @patch.dict('os.environ', {'LOG_API_REQUESTS': 'invalid'})
    def test_invalid_boolean_environment_variable(self):
        """Test handling of invalid boolean environment variable."""
        config = OpenAlexConfig()
        # Should default to False for any value other than 'true' (case insensitive)
        assert config.log_api_requests is False

    @patch.dict('os.environ', {'OPENALEX_TIMEOUT': '45.5'})
    def test_float_environment_variable_parsing(self):
        """Test parsing of float environment variable."""
        config = OpenAlexConfig()
        assert config.timeout == 45.5

    @patch.dict('os.environ', {'OPENALEX_MAX_CONCURRENT': '15'})
    def test_int_environment_variable_parsing(self):
        """Test parsing of integer environment variable."""
        config = OpenAlexConfig()
        assert config.max_concurrent_requests == 15
