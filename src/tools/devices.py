"""Device management tools for Spotify MCP server."""

import logging
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_device_tools(mcp, spotify_client):
    """Register device management tools with the FastMCP server."""

    @mcp.tool()
    @handle_spotify_errors
    async def get_devices() -> str:
        """Get list of available Spotify devices."""
        logger.info("Getting available devices")
        return spotify_client.get_devices()

    @mcp.tool()
    @handle_spotify_errors
    async def is_active_device() -> str:
        """Check if there's an active Spotify device."""
        logger.info("Checking for active device")
        is_active = spotify_client.is_active_device()
        return f"Active device: {is_active}"
