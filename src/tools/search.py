"""Search and queue tools for Spotify MCP server."""

import logging
from helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_search_tools(mcp, spotify_client):
    """Register search and queue tools with the FastMCP server."""

    @mcp.tool()
    @handle_spotify_errors
    async def search_spotify(query: str, qtype: str = "track", limit: int = 10) -> str:
        """
        Search for tracks, albums, artists, or playlists on Spotify.

        Args:
            query: Search query term.
            qtype: Type of items to search for (track, album, artist, playlist,
                   or comma-separated combination).
            limit: Maximum number of items to return (default: 10).
        """
        logger.info(f"Searching: query='{query}', type={qtype}, limit={limit}")
        return spotify_client.search(query=query, qtype=qtype, limit=limit)

    @mcp.tool()
    @handle_spotify_errors
    async def add_to_queue(track_id: str) -> str:
        """
        Add a track to the playback queue.

        Args:
            track_id: Spotify track ID to add to queue.
        """
        logger.info(f"Adding track to queue: {track_id}")
        spotify_client.add_to_queue(track_id)
        return "Track added to queue."

    @mcp.tool()
    @handle_spotify_errors
    async def get_queue() -> str:
        """Get the current playback queue."""
        logger.info("Getting current queue")
        return spotify_client.get_queue()

    @mcp.tool()
    @handle_spotify_errors
    async def get_item_info(item_uri: str) -> str:
        """
        Get detailed information about a Spotify item (track, album, artist, or playlist).

        Args:
            item_uri: URI of the item to get information about.
                     If 'playlist' or 'album', returns its tracks.
                     If 'artist', returns albums and top tracks.
        """
        logger.info(f"Getting info for: {item_uri}")
        return spotify_client.get_info(item_uri)
