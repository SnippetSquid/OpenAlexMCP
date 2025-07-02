"""Configuration management for OpenAlex MCP Server."""

import os
from typing import Optional


class OpenAlexConfig:
    """Configuration for OpenAlex MCP Server."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.email: Optional[str] = os.getenv("OPENALEX_EMAIL")
        self.timeout: float = float(os.getenv("OPENALEX_TIMEOUT", "30.0"))
        self.max_concurrent_requests: int = int(os.getenv("OPENALEX_MAX_CONCURRENT", "10"))
        self.default_page_size: int = int(os.getenv("OPENALEX_DEFAULT_PAGE_SIZE", "25"))
        self.max_page_size: int = int(os.getenv("OPENALEX_MAX_PAGE_SIZE", "200"))

        # Rate limiting
        self.daily_request_limit: int = int(os.getenv("OPENALEX_DAILY_LIMIT", "100000"))

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_api_requests: bool = os.getenv("LOG_API_REQUESTS", "false").lower() == "true"

    def validate(self) -> None:
        """Validate configuration."""
        if self.timeout <= 0:
            raise ValueError("OPENALEX_TIMEOUT must be positive")

        if self.max_concurrent_requests <= 0:
            raise ValueError("OPENALEX_MAX_CONCURRENT must be positive")

        if self.default_page_size <= 0 or self.default_page_size > self.max_page_size:
            raise ValueError(f"OPENALEX_DEFAULT_PAGE_SIZE must be between 1 and {self.max_page_size}")

        if self.daily_request_limit <= 0:
            raise ValueError("OPENALEX_DAILY_LIMIT must be positive")

    def get_user_agent(self) -> str:
        """Get user agent string for API requests."""
        base = "OpenAlexMCP/0.1.0"
        if self.email:
            return f"{base} (mailto:{self.email})"
        return base

    def should_use_polite_pool(self) -> bool:
        """Check if we should use the polite pool (email provided)."""
        return bool(self.email)


# Global config instance
config = OpenAlexConfig()
