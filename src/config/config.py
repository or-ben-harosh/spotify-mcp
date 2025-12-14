"""Configuration module for Spotify MCP server."""

import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging configuration for the server.

    Args:
        level: Logging level (default: INFO)

    Returns:
        Logger instance
    """
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def validate_environment() -> bool:
    """
    Validate that required environment variables are set.

    Returns:
        True if all required variables are set, False otherwise
    """

    required_vars = [
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET',
        'SPOTIFY_REDIRECT_URI'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger = logging.getLogger(__name__)
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False

    return True


class SpotifyConfig:
    """Configuration class for Spotify settings."""

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    @property
    def is_valid(self) -> bool:
        """Check if all required config values are present."""
        return all([self.client_id, self.client_secret, self.redirect_uri])
