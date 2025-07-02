"""OpenAlex API client for making HTTP requests to the OpenAlex API."""

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from .config import config
from .logutil import logger


class OpenAlexClient:
    """Async client for the OpenAlex API."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: Optional[str] = None, timeout: Optional[float] = None):
        """Initialize the OpenAlex client.
        
        Args:
            email: Email address for polite pool access (recommended)
            timeout: Request timeout in seconds
        """
        self.email = email or config.email
        self._timeout = timeout  # Store original value, use property for dynamic config access
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limiter = asyncio.Semaphore(config.max_concurrent_requests)

    @property
    def timeout(self) -> float:
        """Get timeout value, using config if not set explicitly."""
        return self._timeout if self._timeout is not None else config.timeout

    async def __aenter__(self) -> "OpenAlexClient":
        """Async context manager entry."""
        headers = {"User-Agent": config.get_user_agent()}
        self._client = httpx.AsyncClient(timeout=self.timeout, headers=headers)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build the full URL with query parameters."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        if params is None:
            params = {}

        # Add email for polite pool access
        if self.email:
            params["mailto"] = self.email

        if params:
            url += f"?{urlencode(params, doseq=True)}"

        return url

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an async HTTP request to the OpenAlex API."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        async with self._rate_limiter:
            url = self._build_url(endpoint, params)

            if config.log_api_requests:
                logger.debug(f"Making request to: {url}")

            try:
                response = await self._client.get(url)
                response.raise_for_status()

                if config.log_api_requests:
                    logger.debug(f"Response status: {response.status_code}")

                return response.json()
            except httpx.HTTPStatusError as e:
                error_msg = f"OpenAlex API error ({e.response.status_code}): {e.response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except httpx.RequestError as e:
                error_msg = f"Request failed: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)

    async def get_works(
        self,
        work_id: Optional[str] = None,
        search: Optional[str] = None,
        filter_params: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get works from OpenAlex.
        
        Args:
            work_id: Specific work ID to retrieve
            search: Search query
            filter_params: Filter parameters
            sort: Sort order
            page: Page number
            per_page: Results per page
            select: Fields to select
        """
        if work_id:
            endpoint = f"works/{work_id}"
            params: Dict[str, Any] = {}
        else:
            endpoint = "works"
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)  # Max 200 per page
            }
            if search:
                params["search"] = search  # OpenAlex expects 'search' not 'q' for /works
            if sort:
                params["sort"] = sort
            if select:
                params["select"] = ",".join(select)
            if filter_params:
                filters = []
                for key, value in filter_params.items():
                    filters.append(f"{key}:{value}")
                if filters:
                    params["filter"] = ",".join(filters)

        return await self._make_request(endpoint, params)

    async def get_authors(
        self,
        author_id: Optional[str] = None,
        search: Optional[str] = None,
        filter_params: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get authors from OpenAlex."""
        if author_id:
            endpoint = f"authors/{author_id}"
            params: Dict[str, Any] = {}
        else:
            endpoint = "authors"
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)
            }
            if search:
                params["search"] = search
            if sort:
                params["sort"] = sort
            if select:
                params["select"] = ",".join(select)
            if filter_params:
                filters = []
                for key, value in filter_params.items():
                    filters.append(f"{key}:{value}")
                if filters:
                    params["filter"] = ",".join(filters)

        return await self._make_request(endpoint, params)

    async def get_institutions(
        self,
        institution_id: Optional[str] = None,
        search: Optional[str] = None,
        filter_params: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get institutions from OpenAlex."""
        if institution_id:
            endpoint = f"institutions/{institution_id}"
            params: Dict[str, Any] = {}
        else:
            endpoint = "institutions"
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)
            }
            if search:
                params["search"] = search
            if sort:
                params["sort"] = sort
            if select:
                params["select"] = ",".join(select)
            if filter_params:
                filters = []
                for key, value in filter_params.items():
                    filters.append(f"{key}:{value}")
                if filters:
                    params["filter"] = ",".join(filters)

        return await self._make_request(endpoint, params)

    async def get_sources(
        self,
        source_id: Optional[str] = None,
        search: Optional[str] = None,
        filter_params: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get sources from OpenAlex."""
        if source_id:
            endpoint = f"sources/{source_id}"
            params: Dict[str, Any] = {}
        else:
            endpoint = "sources"
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)
            }
            if search:
                params["search"] = search
            if sort:
                params["sort"] = sort
            if select:
                params["select"] = ",".join(select)
            if filter_params:
                filters = []
                for key, value in filter_params.items():
                    filters.append(f"{key}:{value}")
                if filters:
                    params["filter"] = ",".join(filters)

        return await self._make_request(endpoint, params)

    async def get_topics(
        self,
        topic_id: Optional[str] = None,
        search: Optional[str] = None,
        filter_params: Optional[Dict[str, str]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        per_page: int = 25,
        select: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get topics from OpenAlex."""
        if topic_id:
            endpoint = f"topics/{topic_id}"
            params: Dict[str, Any] = {}
        else:
            endpoint = "topics"
            params: Dict[str, Any] = {
                "page": page,
                "per_page": min(per_page, 200)
            }
            if search:
                params["search"] = search
            if sort:
                params["sort"] = sort
            if select:
                params["select"] = ",".join(select)
            if filter_params:
                filters = []
                for key, value in filter_params.items():
                    filters.append(f"{key}:{value}")
                if filters:
                    params["filter"] = ",".join(filters)

        return await self._make_request(endpoint, params)

    async def download_pdf(self, pdf_url: str, file_path: str) -> bool:
        """Download a PDF from a given URL.
        
        Args:
            pdf_url: URL of the PDF to download
            file_path: Local path where to save the PDF
            
        Returns:
            True if download was successful, False otherwise
        """
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        try:
            async with self._rate_limiter:
                if config.log_api_requests:
                    logger.debug(f"Downloading PDF from: {pdf_url}")

                response = await self._client.get(pdf_url, follow_redirects=True)
                response.raise_for_status()

                # Check if response contains PDF content
                content_type = response.headers.get("content-type", "").lower()
                if "pdf" not in content_type:
                    logger.warning(f"Downloaded content may not be PDF: {content_type}")

                with open(file_path, "wb") as f:
                    f.write(response.content)

                if config.log_api_requests:
                    logger.debug(f"PDF saved to: {file_path}")

                return True

        except httpx.HTTPStatusError as e:
            error_msg = f"PDF download failed ({e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            return False
        except httpx.RequestError as e:
            error_msg = f"PDF download request failed: {str(e)}"
            logger.error(error_msg)
            return False
        except OSError as e:
            error_msg = f"Failed to save PDF file: {str(e)}"
            logger.error(error_msg)
            return False
