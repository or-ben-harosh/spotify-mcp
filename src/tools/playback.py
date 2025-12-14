"""Playback control tools for Spotify MCP server."""

import logging
from typing import Optional
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_playback_tools(mcp, spotify_client):
    """Register playback control tools with the FastMCP server."""

    @mcp.tool()
    @handle_spotify_errors
    async def get_current_track() -> str:
        """Get information about user's current track."""
        logger.info("Getting current track")
        curr_track = spotify_client.get_current_track()
        return curr_track if curr_track else "No track playing."

    @mcp.tool()
    @handle_spotify_errors
    async def start_playback(spotify_uri: Optional[str] = None) -> str:
        """
        Start playback of a Spotify URI or resume current playback.

        Args:
            spotify_uri: Spotify URI of item to play (e.g., "spotify:track:xxxxx").
                        If omitted, resumes current playback.
        """
        logger.info(f"Starting playback: {spotify_uri}")
        spotify_client.start_playback(spotify_uri=spotify_uri)
        return "Playback started."

    @mcp.tool()
    @handle_spotify_errors
    async def pause_playback() -> str:
        """Pause current playback."""
        logger.info("Pausing playback")
        spotify_client.pause_playback()
        return "Playback paused."

    @mcp.tool()
    @handle_spotify_errors
    async def skip_tracks(num_skips: int = 1) -> str:
        """
        Skip current track(s).

        Args:
            num_skips: Number of tracks to skip (default: 1).
        """
        logger.info(f"Skipping {num_skips} tracks")
        spotify_client.skip_track(n=num_skips)
        return f"Skipped {num_skips} track(s)."

    @mcp.tool()
    @handle_spotify_errors
    async def previous_track() -> str:
        """Go to the previous track."""
        logger.info("Going to previous track")
        spotify_client.previous_track()
        return "Switched to previous track."

    @mcp.tool()
    @handle_spotify_errors
    async def set_volume(volume_percent: int) -> str:
        """
        Set the playback volume.

        Args:
            volume_percent: Volume level as percentage (0-100).
        """
        logger.info(f"Setting volume to {volume_percent}%")
        if volume_percent < 0 or volume_percent > 100:
            return "Error: Volume must be between 0 and 100."
        
        spotify_client.set_volume(volume_percent)
        return f"Volume set to {volume_percent}%."

    @mcp.tool()
    @handle_spotify_errors
    async def seek_to_position(position_ms: int) -> str:
        """
        Seek to a position in the current track.

        Args:
            position_ms: Position in milliseconds to seek to.
        """
        logger.info(f"Seeking to position {position_ms}ms")
        spotify_client.seek_to_position(position_ms)
        return f"Seeked to position {position_ms}ms."
