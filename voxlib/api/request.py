from .errors import *
from .endpoints import VoxylApiEndpoint
import asyncio
from os import getenv
from aiohttp import (
    ClientError,
    ServerTimeoutError,
    ContentTypeError,
    ClientSession
)
from aiohttp.client_exceptions import InvalidURL, ClientConnectorError
from aiohttp_client_cache import CachedSession, SQLiteBackend

from dotenv import load_dotenv
load_dotenv()


API_KEY = getenv("API_KEY")

voxyl_cache = SQLiteBackend(
    cache_name="voxlib/.cache/voxyl_cache", expire_after=300,
)


class VoxylAPI:
    """
    Asynchronous client for interacting with the Voxyl Network API.

    This client provides:
      - Automatic API key injection
      - Optional request caching (via aiohttp-client-cache)
      - Retry logic for transient errors
      - Custom exceptions for rate limits, bad requests, and unexpected statuses
    """

    def __init__(self, api_key: str = API_KEY):
        """
        Initialize the VoxylAPI client.

        Args:
            api_key (str, optional): API key for authenticating requests.
                If not provided, defaults to the environment variable `API_KEY`.
        """
        self.base_url: str = "https://api.voxyl.net"
        self.api_key: str = api_key

    async def _make_request(
        self,
        session: ClientSession | CachedSession,
        endpoint: VoxylApiEndpoint,
        **kwargs,
    ):        
        """
        Internal helper that executes a single GET request to the Voxyl API.

        Args:
            session (aiohttp.ClientSession | aiohttp_client_cache.CachedSession):
                Active session used to make the request.
            endpoint (VoxylApiEndpoint): Enum value representing the API route.
            **kwargs: Path variables to format into the endpoint, and extra query parameters.

        Raises:
            RateLimitError: If the API rate limit is exceeded (HTTP 429).
            UnexpectedStatusError: If the API returns an unexpected status code.
            APIError: For connection issues, invalid URLs, timeouts, or other client errors.

        Returns:
            dict | str | None: Parsed JSON response if available, raw text if not JSON,
                or None if the API returned HTTP 400.
        """
        url: str = f"{self.base_url}/{endpoint.value.format(**kwargs)}"

        params: dict = {"api": self.api_key}
        params.update(kwargs)

        try:
            async with session.get(url=url, params=params) as response:
                try:
                    content = await response.json(content_type=None)
                except Exception:
                    content = await response.text()

                if response.status == 200:
                    return content
                elif response.status == 400:
                    return None
                elif response.status == 429:
                    raise RateLimitError(f"Rate limit exceeded: {content}")
                else:
                    raise UnexpectedStatusError(
                        f"Unexpected status {response.status}: {content}"
                    )

        except (ClientConnectorError, InvalidURL) as error:
            raise APIError(f"Connection error: {error}")
        except ServerTimeoutError:
            raise APIError("Server timeout occurred")
        except ClientError as error:
            raise APIError(f"HTTP client error: {error}")
        except ContentTypeError as error:
            raise APIError(f"Invalid content type: {error}")
        except Exception as e:
            raise APIError(f"Unexpected error: {e}")

    async def make_request(
        self,
        endpoint: VoxylApiEndpoint,
        cache: bool = True,
        cached_session: SQLiteBackend = voxyl_cache,
        retries: int = 3,
        retry_delay: int = 5,
        **kwargs,
    ):
        """
        Make an asynchronous GET request to the specified Voxyl API endpoint.

        Supports caching, retries, and structured exception handling.

        Args:
            endpoint (VoxylApiEndpoint): API endpoint enum value.
            cache (bool, optional): Whether to use a cached session. Defaults to True.
            cached_session (SQLiteBackend, optional): Cache backend to use if caching
                is enabled. Defaults to `voxyl_cache` (5 min expiry).
            retries (int, optional): Number of retry attempts for transient failures.
                Defaults to 3.
            retry_delay (int, optional): Delay (in seconds) between retries.
                Defaults to 5.
            **kwargs: Path variables to format into the endpoint, and extra query parameters.

        Returns:
            dict | str | None: Parsed JSON response if available, raw text if not JSON,
                or None if the API returned HTTP 400.

        Raises:
            RateLimitError: If the API rate limit is exceeded (HTTP 429).
            UnexpectedStatusError: If the API returns an unexpected status code.
            APIError: For connection issues, invalid URLs, timeouts, or other client errors.
        """
        for attempt in range(retries + 1):
            try:
                if not cache:
                    async with CachedSession() as session:
                        return await self._make_request(session, endpoint, **kwargs)

                async with CachedSession(cache=cached_session) as session:
                    return await self._make_request(session, endpoint, **kwargs)

            except APIError as exc:
                if attempt < retries:
                    print(
                        f"[VoxylAPI] Request failed ({exc}). "
                        f"Retrying in {retry_delay}s... [Attempt {attempt+1}/{retries}]"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    raise


API = VoxylAPI()
