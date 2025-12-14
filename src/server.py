""" Spotify MCP Server """

import sys
from mcp.server import FastMCP

import spotify_api
from config import setup_logging, validate_environment
from helpers.auth_helpers import normalize_redirect_uri
from tools.playback import register_playback_tools
from tools.search import register_search_tools
from tools.playlists import register_playlist_tools
from tools.devices import register_device_tools

# Setup logging
logger = setup_logging()

# Initialize FastMCP server (early so it can be imported)
mcp = FastMCP("spotify-mcp")

# Initialize Spotify client and register tools at module level
def _initialize_server():
    """Initialize the Spotify client and register tools."""
    # Validate environment on startup
    if not validate_environment():
        logger.error("Environment validation failed. Please check your configuration.")
        return None

    # Normalize the redirect URI to meet Spotify's requirements
    if spotify_api.REDIRECT_URI:
        spotify_api.REDIRECT_URI = normalize_redirect_uri(spotify_api.REDIRECT_URI)

    # Initialize Spotify client
    try:
        spotify_client = spotify_api.Client(logger)
        logger.info("Spotify client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {e}")
        # Don't exit here - let the tools handle auth errors gracefully
        spotify_client = None

    # Register all tools
    if spotify_client:
        register_playback_tools(mcp, spotify_client)
        register_search_tools(mcp, spotify_client)
        register_playlist_tools(mcp, spotify_client)
        register_device_tools(mcp, spotify_client)
        logger.info("All tools registered successfully")

    return spotify_client


# Initialize at module level for mcp dev
spotify_client = _initialize_server()


def main():
    """Main entry point for the Spotify MCP Server."""
    logger.info("Starting Spotify MCP Server")

    # Check if initialization was successful
    if not spotify_client:
        logger.error("Failed to initialize Spotify client. Exiting.")
        sys.exit(1)

    try:
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
