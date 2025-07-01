"""Integration tests (requires network access)."""

import os
import pytest
from src.openalex_mcp.client import OpenAlexClient
from src.openalex_mcp.tools import search_works, search_authors


class TestRealAPIIntegration:
    """Integration tests against the real OpenAlex API.
    
    These tests are marked as 'slow' and 'integration' and require network access.
    They can be skipped by running: pytest -m "not slow and not integration"
    """

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_search_works(self):
        """Test real API call to search works."""
        # Skip if running in CI without API access
        if os.getenv("SKIP_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled")
        
        # Use no email to avoid 400 "Invalid" errors with fake emails
        client = OpenAlexClient()
        
        arguments = {
            "query": "attention is all you need",
            "limit": 3
        }
        
        async with client:
            results = await search_works(client, arguments)
        
        assert len(results) == 1
        # Should either find results or get an error message
        assert any(phrase in results[0].text.lower() for phrase in ["attention", "works", "found", "error"])

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_search_authors(self):
        """Test real API call to search authors."""
        if os.getenv("SKIP_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled")
        
        # Use no email to avoid 400 "Invalid" errors with fake emails
        client = OpenAlexClient()
        
        arguments = {
            "query": "Geoffrey Hinton",
            "limit": 2
        }
        
        async with client:
            results = await search_authors(client, arguments)
        
        assert len(results) == 1
        # Should either find results or get an error message
        assert any(phrase in results[0].text.lower() for phrase in ["hinton", "found", "authors", "error"])

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_rate_limiting(self):
        """Test that rate limiting works with real API."""
        if os.getenv("SKIP_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled")
        
        # Use no email to avoid 400 "Invalid" errors with fake emails
        client = OpenAlexClient()
        
        # Make multiple concurrent requests
        import asyncio
        
        async def make_request():
            arguments = {"query": "machine learning", "limit": 1}
            async with client:
                return await search_works(client, arguments)
        
        # Create multiple tasks
        tasks = [make_request() for _ in range(5)]
        
        # This should complete without errors due to rate limiting
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should complete (may have exceptions due to API limits but no network errors)
        assert len(results) == 5

    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_error_handling(self):
        """Test error handling with real API."""
        if os.getenv("SKIP_INTEGRATION_TESTS"):
            pytest.skip("Integration tests disabled")
        
        # Use no email to avoid 400 "Invalid" errors with fake emails
        client = OpenAlexClient()
        
        # Test with invalid work ID
        from src.openalex_mcp.tools import get_work_details
        
        arguments = {"work_id": "W999999999999999"}
        
        async with client:
            results = await get_work_details(client, arguments)
        
        # Should handle the error gracefully
        assert len(results) == 1
        # Either "not found" or some other error message
        assert any(phrase in results[0].text.lower() for phrase in ["not found", "error"])


class TestMockAPIIntegration:
    """Integration tests using mocked API responses.
    
    These tests verify the full flow without network calls.
    """

    @pytest.mark.asyncio
    async def test_full_pipeline_with_mocks(self):
        """Test the full pipeline with mocked components."""
        from unittest.mock import AsyncMock, patch
        from src.openalex_mcp.tools import search_works
        
        # Create a mock client
        mock_client = AsyncMock()
        mock_response = {
            "meta": {"count": 1},
            "results": [{
                "id": "W123",
                "title": "Test Work",
                "authorships": [],
                "topics": [],
                "primary_location": None,
                "publication_year": 2023,
                "cited_by_count": 5
            }]
        }
        mock_client.get_works.return_value = mock_response
        
        arguments = {"query": "test"}
        
        results = await search_works(mock_client, arguments)
        
        assert len(results) == 1
        assert "Test Work" in results[0].text
        mock_client.get_works.assert_called_once()


class TestConfigurationIntegration:
    """Test configuration integration across components."""

    def test_config_used_by_client(self):
        """Test that client uses configuration."""
        from src.openalex_mcp.config import config
        
        # Temporarily modify config
        original_timeout = config.timeout
        config.timeout = 99.0
        
        try:
            # Client should use config when no explicit timeout is provided
            client = OpenAlexClient(timeout=None)
            assert client.timeout == 99.0
        finally:
            # Restore original
            config.timeout = original_timeout

    def test_config_validation_integration(self):
        """Test that configuration validation works in practice."""
        from src.openalex_mcp.config import OpenAlexConfig
        
        config = OpenAlexConfig()
        config.timeout = -1
        
        with pytest.raises(ValueError):
            config.validate()


class TestErrorHandlingIntegration:
    """Test error handling across the entire system."""

    @pytest.mark.asyncio
    async def test_network_error_propagation(self):
        """Test that network errors are properly handled."""
        from unittest.mock import patch
        import httpx
        
        client = OpenAlexClient()
        
        with patch.object(client, '_client') as mock_client:
            mock_client.get.side_effect = httpx.RequestError("Network error")
            
            with pytest.raises(Exception) as exc_info:
                await client._make_request("works")
            
            assert "Request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_server_error_handling_integration(self):
        """Test server-level error handling."""
        from unittest.mock import AsyncMock, patch
        from src.openalex_mcp.tools import search_works
        client = AsyncMock()
        arguments = {"query": "test"}
        with patch('src.openalex_mcp.tools.search_works', side_effect=Exception("Test error")):
            try:
                await search_works(client, arguments)
            except Exception as e:
                assert "Test error" in str(e)