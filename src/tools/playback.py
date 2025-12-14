"""Playback control tools for Spotify MCP server - Improved with Context"""

import logging
from typing import Optional
from mcp.server.fastmcp import Context
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_playback_tools(mcp, spotify_client):
    """Register playback control tools with the FastMCP server."""

    @mcp.tool(
        description="Get information about the currently playing track"
    )
    @handle_spotify_errors
    async def get_current_track(ctx: Context) -> str:
        """Get information about user's current track."""
        await ctx.info("Getting current track")
        curr_track = spotify_client.get_current_track()
        return curr_track if curr_track else "No track playing."

    @mcp.tool(
        description="Start or resume playback on Spotify"
    )
    @handle_spotify_errors
    async def start_playback(spotify_uri: Optional[str] = None, ctx: Context = None) -> str:
        """
        Start playback of a Spotify URI or resume current playback.

        Args:
            spotify_uri: Spotify URI of item to play (e.g., "spotify:track:xxxxx").
                        If omitted, resumes current playback.
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Starting playback: {spotify_uri or 'resuming'}")
        spotify_client.start_playback(spotify_uri=spotify_uri)
        return "Playback started."

    @mcp.tool(
        description="Pause the current playback"
    )
    @handle_spotify_errors
    async def pause_playback(ctx: Context) -> str:
        """Pause current playback."""
        await ctx.info("Pausing playback")
        spotify_client.pause_playback()
        return "Playback paused."

    @mcp.tool(
        description="Skip forward one or more tracks"
    )
    @handle_spotify_errors
    async def skip_tracks(num_skips: int, ctx: Context) -> str:
        """
        Skip current track(s).

        Args:
            num_skips: Number of tracks to skip (default: 1).
            ctx: MCP context for logging
        """
        await ctx.info(f"Skipping {num_skips} track(s)")
        spotify_client.skip_track(n=num_skips)
        return f"Skipped {num_skips} track(s)."

    @mcp.tool(
        description="Go back to the previous track"
    )
    @handle_spotify_errors
    async def previous_track(ctx: Context) -> str:
        """Go to the previous track."""
        await ctx.info("Going to previous track")
        spotify_client.previous_track()
        return "Switched to previous track."

    @mcp.tool(
        description="Set playback volume (0-100)"
    )
    @handle_spotify_errors
    async def set_volume(volume_percent: int, ctx: Context) -> str:
        """
        Set the playback volume.

        Args:
            volume_percent: Volume level as percentage (0-100).
            ctx: MCP context for logging
        """
        await ctx.info(f"Setting volume to {volume_percent}%")
        if volume_percent < 0 or volume_percent > 100:
            return "Error: Volume must be between 0 and 100."

        spotify_client.set_volume(volume_percent)
        return f"Volume set to {volume_percent}%."

    @mcp.tool(
        description="Seek to a specific position in the current track"
    )
    @handle_spotify_errors
    async def seek_to_position(position_ms: int, ctx: Context) -> str:
        """
        Seek to a position in the current track.

        Args:
            position_ms: Position in milliseconds to seek to.
            ctx: MCP context for logging
        """
        await ctx.info(f"Seeking to position {position_ms}ms")
        spotify_client.seek_to_position(position_ms)
        return f"Seeked to position {position_ms}ms."
