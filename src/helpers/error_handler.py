"""Error handling utilities for Spotify MCP server."""

import functools
import json
import logging
from typing import Callable, TypeVar
from spotipy import SpotifyException

logger = logging.getLogger(__name__)

T = TypeVar('T')


def handle_spotify_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle Spotify API errors consistently across tools.
    Returns formatted error messages instead of raising exceptions.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            # If result is a dict or list, convert to JSON
            if isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            return result
        except SpotifyException as se:
            error_msg = f"Spotify API error: {str(se)}"
            logger.error(error_msg)
            return error_msg
        except ValueError as ve:
            error_msg = f"Validation error: {str(ve)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg
    
    return wrapper
