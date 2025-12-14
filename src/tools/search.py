"""Search and queue tools for Spotify MCP server - Improved with Context"""

import logging
from mcp.server.fastmcp import Context
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_search_tools(mcp, spotify_client):
    """Register search and queue tools with the FastMCP server."""

    @mcp.tool(
        description="Search for tracks, albums, artists, or playlists on Spotify"
    )
    @handle_spotify_errors
    async def search_spotify(query: str, qtype: str = "track", limit: int = 10, ctx: Context = None) -> str:
        """
        Search for tracks, albums, artists, or playlists on Spotify.

        Args:
            query: Search query term.
            qtype: Type of items to search for (track, album, artist, playlist,
                   or comma-separated combination).
            limit: Maximum number of items to return (default: 10).
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Searching: query='{query}', type={qtype}, limit={limit}")
        return spotify_client.search(query=query, qtype=qtype, limit=limit)


    @mcp.tool(
        description="Add a track to the playback queue"
    )
    @handle_spotify_errors
    async def add_to_queue(track_id: str, ctx: Context = None) -> str:
        """
        Add a track to the playback queue.

        Args:
            track_id: Spotify track ID to add to queue.
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Adding track to queue: {track_id}")
        spotify_client.add_to_queue(track_id)
        return "Track added to queue."


    @mcp.tool(
        description="Get the current playback queue"
    )
    @handle_spotify_errors
    async def get_queue(ctx: Context) -> str:
        """Get the current playback queue."""
        await ctx.info("Getting current queue")
        return spotify_client.get_queue()


    @mcp.tool(
        description="Get detailed information about a Spotify item (track, album, artist, or playlist)"
    )
    @handle_spotify_errors
    async def get_item_info(item_uri: str, ctx: Context = None) -> str:
        """
        Get detailed information about a Spotify item (track, album, artist, or playlist).

        Args:
            item_uri: URI of the item to get information about.
                     If 'playlist' or 'album', returns its tracks.
                     If 'artist', returns albums and top tracks.
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Getting info for: {item_uri}")
        return spotify_client.get_info(item_uri)