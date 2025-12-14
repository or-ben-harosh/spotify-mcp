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
        if not self.auth_ok():
            self.auth_refresh()
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
    """Refresh authentication token."""
    auth_manager.validate_token(cache_handler.get_cached_token())
