"""Authentication helpers for Spotify client."""

import functools
import logging
from typing import Callable, TypeVar
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)

T = TypeVar('T')


def normalize_redirect_uri(url: str) -> str:
    """
    Normalize redirect URI to meet Spotify's requirements.
    Converts localhost to 127.0.0.1.

    Args:
        url: The redirect URI to normalize

    Returns:
        Normalized redirect URI
    """
    if not url:
        return url

    parsed = urlparse(url)

    # Convert localhost to 127.0.0.1
    if parsed.netloc == 'localhost' or parsed.netloc.startswith('localhost:'):
        port = ''
        if ':' in parsed.netloc:
            port = ':' + parsed.netloc.split(':')[1]
        parsed = parsed._replace(netloc=f'127.0.0.1{port}')

    return str(urlunparse(parsed))


def ensure_auth(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to ensure authentication is valid before API calls."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Get cached token and validate it
        token_info = self.auth_manager.get_cached_token()

        if token_info is None:
            # No token cached - need initial authentication
            raise RuntimeError(
                "No authentication token found. Please run initial authentication first.\n"
                "The browser should have opened during server startup for authentication."
            )

        # Check if token is expired and refresh if needed
        if self.auth_manager.is_token_expired(token_info):
            logger.info("Token expired, refreshing...")
            # This will refresh without opening browser
            token_info = self.auth_manager.refresh_access_token(token_info['refresh_token'])

        return func(self, *args, **kwargs)

    return wrapper


def ensure_username(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to ensure username is set before calling function."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.username is None:
            self.set_username()
        return func(self, *args, **kwargs)

    return wrapper


def check_token(auth_manager, cache_handler) -> bool:
    """Check if authentication token is valid."""
    try:
        token = cache_handler.get_cached_token()
        if token is None:
            logger.info("No auth token found")
            return False

        is_expired = auth_manager.is_token_expired(token)
        logger.info(f"Auth token is {'expired' if is_expired else 'valid'}")
        return not is_expired
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return False


def refresh_token(auth_manager, cache_handler):
    """Refresh authentication token without opening browser."""
    try:
        token = cache_handler.get_cached_token()
        if token and 'refresh_token' in token:
            # Use refresh_access_token instead of validate_token
            # This refreshes without triggering OAuth flow
            new_token = auth_manager.refresh_access_token(token['refresh_token'])
            logger.info("Token refreshed successfully")
            return new_token
        else:
            logger.error("Cannot refresh token - no refresh token available")
            raise RuntimeError("No refresh token available. Please authenticate again.")
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise