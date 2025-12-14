"""Playlist management tools for Spotify MCP server - Improved with Context"""

import logging
from typing import List, Optional
from mcp.server.fastmcp import Context
from src.helpers.error_handler import handle_spotify_errors

logger = logging.getLogger(__name__)


def register_playlist_tools(mcp, spotify_client):
    """Register playlist management tools with the FastMCP server."""

    @mcp.tool(
        description="Get current user's playlists"
    )
    @handle_spotify_errors
    async def get_user_playlists(ctx: Context) -> str:
        """Get current user's playlists."""
        await ctx.info("Getting user playlists")
        return spotify_client.get_current_user_playlists()


    @mcp.tool(
        description="Get tracks from a specific playlist"
    )
    @handle_spotify_errors
    async def get_playlist_tracks(playlist_id: str, ctx: Context) -> str:
        """
        Get tracks from a specific playlist.

        Args:
            playlist_id: ID of the playlist to get tracks from.
            ctx: MCP context for logging
        """
        await ctx.info(f"Getting tracks from playlist: {playlist_id}")

        if not playlist_id:
            return "Error: playlist_id is required."
        return spotify_client.get_playlist_tracks(playlist_id)


    @mcp.tool(
        description="Add tracks to a specific playlist"
    )
    @handle_spotify_errors
    async def add_tracks_to_playlist(playlist_id: str, track_ids: List[str], ctx: Context) -> str:
        """
        Add tracks to a specific playlist.

        Args:
            playlist_id: ID of the playlist to add tracks to.
            track_ids: List of track IDs to add to the playlist.
            ctx: MCP context for logging
        """
        await ctx.info(f"Adding {len(track_ids)} tracks to playlist {playlist_id}")

        if not playlist_id or not track_ids:
            return "Error: playlist_id and track_ids are required."

        spotify_client.add_tracks_to_playlist(playlist_id=playlist_id, track_ids=track_ids)
        return "Tracks added to playlist."


    @mcp.tool(
        description="Remove tracks from a specific playlist"
    )
    @handle_spotify_errors
    async def remove_tracks_from_playlist(playlist_id: str, track_ids: List[str], ctx: Context) -> str:
        """
        Remove tracks from a specific playlist.

        Args:
            playlist_id: ID of the playlist to remove tracks from.
            track_ids: List of track IDs to remove from the playlist.
            ctx: MCP context for logging
        """
        await ctx.info(f"Removing {len(track_ids)} tracks from playlist {playlist_id}")

        if not playlist_id or not track_ids:
            return "Error: playlist_id and track_ids are required."

        spotify_client.remove_tracks_from_playlist(playlist_id=playlist_id, track_ids=track_ids)
        return "Tracks removed from playlist."


    @mcp.tool(
        description="Create a new playlist"
    )
    @handle_spotify_errors
    async def create_playlist(name: str, description: Optional[str] = None, public: bool = True, ctx: Context = None) -> str:
        """
        Create a new playlist.

        Args:
            name: Name for the new playlist.
            description: Optional description for the playlist.
            public: Whether the playlist should be public (default: True).
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Creating playlist: {name}")
        if not name:
            return "Error: name is required for creating a playlist."

        return spotify_client.create_playlist(name=name, description=description, public=public)

    @mcp.tool(
        description="Change playlist details (name and/or description)"
    )
    @handle_spotify_errors
    async def change_playlist_details(
        playlist_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        ctx: Context = None
    ) -> str:
        """
        Change playlist details (name and/or description).

        Args:
            playlist_id: ID of the playlist to modify.
            name: New name for the playlist (optional).
            description: New description for the playlist (optional).
            ctx: MCP context for logging
        """
        if ctx:
            await ctx.info(f"Changing playlist details for {playlist_id}")
        if not playlist_id:
            return "Error: playlist_id is required."

        spotify_client.change_playlist_details(
            playlist_id=playlist_id,
            name=name,
            description=description
        )
        return "Playlist details updated."