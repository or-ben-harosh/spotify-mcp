"""
Spotify MCP Server - Improved with FastMCP best practices
"""

import sys
from mcp.server import FastMCP
from src.helpers.auth_helpers import normalize_redirect_uri
from src.api import spotify_api
from src.config.config import validate_environment, setup_logging
from src.tools.playback import register_playback_tools
from src.tools.search import register_search_tools
from src.tools.playlists import register_playlist_tools
from src.tools.devices import register_device_tools

# Setup logging
logger = setup_logging()

# Initialize FastMCP server
mcp = FastMCP("spotify-mcp")

# Initialize Spotify client and register tools
def _initialize_server():
    """Initialize the Spotify client and register tools."""
    if not validate_environment():
        logger.error("Environment validation failed. Please check your configuration.")
        return None

    if spotify_api.REDIRECT_URI:
        spotify_api.REDIRECT_URI = normalize_redirect_uri(spotify_api.REDIRECT_URI)

    try:
        spotify_client = spotify_api.Client(logger)
        logger.info("Spotify client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {e}")
        return None

    # Register all tools with context support
    if spotify_client:
        register_playback_tools(mcp, spotify_client)
        register_search_tools(mcp, spotify_client)
        register_playlist_tools(mcp, spotify_client)
        register_device_tools(mcp, spotify_client)
        logger.info("All tools registered successfully")

    return spotify_client


spotify_client = _initialize_server()


def main():
    """Main entry point for the Spotify MCP Server."""
    logger.info("Starting Spotify MCP Server")

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

if __name__ == "__main__":
    main()