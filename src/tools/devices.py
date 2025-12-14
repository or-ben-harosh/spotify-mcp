"""Device management tools for Spotify MCP server."""

import logging
from mcp.server.fastmcp import Context
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_device_tools(mcp, spotify_client):
    """Register device management tools with the FastMCP server."""

    @mcp.tool(description="Get a list of all available Spotify devices including computers, phones, tablets, and speakers. Shows device name, type, ID, active status, and volume level.")
    @handle_spotify_errors
    async def get_devices(ctx: Context) -> str:
        """Get list of available Spotify devices."""
        await ctx.info("Getting available devices")
        return spotify_client.get_devices()

    @mcp.tool(description="Check if there is currently an active Spotify device ready to play music. Returns true if a device is active, false if you need to open Spotify on a device first.")
    @handle_spotify_errors
    async def is_active_device(ctx: Context) -> str:
        "Check if there's an active Spotify device."""
        await ctx.info("Checking for active device")
        is_active = spotify_client.is_active_device()
        return f"Active device: {is_active}"