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
from typing import Literal
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import InvalidURL, ClientConnectorError
from aiohttp_client_cache import CachedSession, SQLiteBackend

from dotenv import load_dotenv
load_dotenv()


API_KEY = getenv("API_KEY")

voxyl_cache = SQLiteBackend(
    cache_name="voxlib/.cache/voxyl_cache", expire_after=300,
)

skin_session = SQLiteBackend(
    cache_name=f'voxlib/.cache/skin_cache', expire_after=900
)


class VoxylAPI:
    """
    Asynchronous client for interacting with the Voxyl Network API.
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
        params.update({k: v for k, v in kwargs.items() if v is not None})

        try:
            response = await session.get(url=url, params=params)

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


SkinStyle = Literal[
    'face', 'front', 'frontfull', 'head',
    'bust', 'full', 'skin', 'processedskin'
]

DEFAULT_STEVE_SKIN_URL = (
    "https://textures.minecraft.net/texture/"
    "a4665d6a9c07b7b3ecf3b9f4b1c6bff0e43a9a3b65e5b4b94a3a4567d9a12345"
)

async def fetch_skin_model(
    uuid: str,
    style: SkinStyle = "full"
) -> bytes:
    
    base_url = "https://visage.surgeplay.com"
    headers = {
        "User-Agent": "Vixel Stats Bot Version 1"
    }
    
    timeout = ClientTimeout(total=5)
    url = f"{base_url}/{style}/512/{uuid}"

    try:
        async with CachedSession(cache=skin_session) as session:
            res = await session.get(url, headers=headers, timeout=timeout)
            if res.status == 200:
                return await res.read()
            else:
                async with CachedSession(cache=skin_session) as fallback_session:
                    fallback_res = await fallback_session.get(
                        DEFAULT_STEVE_SKIN_URL, headers=headers, timeout=timeout
                    )
                    return await fallback_res.read()

    except Exception:
        async with CachedSession(cache=skin_session) as fallback_session:
            fallback_res = await fallback_session.get(
                DEFAULT_STEVE_SKIN_URL, headers=headers, timeout=timeout
            )
            return await fallback_res.read()