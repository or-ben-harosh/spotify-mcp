"""Simplified Spotify API client."""

import logging
import os
from typing import Optional, Dict, List

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from helpers import parsers, auth_helpers, device_helpers
from utils import normalize_redirect_uri

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = normalize_redirect_uri(os.getenv("SPOTIFY_REDIRECT_URI"))

SCOPES = [
    "user-read-currently-playing",
    "user-read-playback-state",
    "app-remote-control",
    "streaming",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-private",
    "playlist-modify-public",
    "user-read-playback-position",
    "user-top-read",
    "user-read-recently-played",
    "user-library-modify",
    "user-library-read",
]


class Client:
    def __init__(self, logger: logging.Logger):
        """Initialize Spotify client with necessary permissions."""
        self.logger = logger
        scope = ",".join(SCOPES)

        try:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    scope=scope,
                    client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    redirect_uri=REDIRECT_URI
                )
            )
            self.auth_manager = self.sp.auth_manager
            self.cache_handler = self.auth_manager.cache_handler
        except Exception as e:
            self.logger.error(f"Failed to initialize Spotify client: {e}")
            raise

        self.username = None

    # ---- Authentication methods ----

    def auth_ok(self) -> bool:
        """Check if authentication token is valid."""
        return auth_helpers.check_token(self.auth_manager, self.cache_handler)

    def auth_refresh(self):
        """Refresh authentication token."""
        auth_helpers.refresh_token(self.auth_manager, self.cache_handler)

    @auth_helpers.ensure_auth
    def set_username(self, device=None):
        """Set the current user's username."""
        self.username = self.sp.current_user()['display_name']

    # ---- Search methods ----

    @auth_helpers.ensure_auth
    def search(self, query: str, qtype: str = 'track', limit=10, device=None):
        """
        Search for items on Spotify.
        
        Args:
            query: Search query term
            qtype: Item types to return ('track', 'album', 'artist', 'playlist' or comma-separated)
            limit: Maximum number of items to return
        """
        if self.username is None:
            self.set_username()
        
        results = self.sp.search(q=query, limit=limit, type=qtype)
        if not results:
            raise ValueError("No search results found.")
        
        return parsers.parse_search_results(results, qtype, self.username)

    def get_info(self, item_uri: str) -> dict:
        """
        Get detailed information about a Spotify item.
        
        Args:
            item_uri: URI like 'spotify:track:xxxxx' or 'spotify:album:xxxxx'
        """
        _, qtype, item_id = item_uri.split(":")
        
        if qtype == 'track':
            return parsers.parse_track(self.sp.track(item_id), detailed=True)
        elif qtype == 'album':
            return parsers.parse_album(self.sp.album(item_id), detailed=True)
        elif qtype == 'artist':
            artist_info = parsers.parse_artist(self.sp.artist(item_id), detailed=True)
            albums = self.sp.artist_albums(item_id)
            top_tracks = self.sp.artist_top_tracks(item_id)['tracks']
            parsed_info = parsers.parse_search_results(
                {'albums': albums, 'tracks': {'items': top_tracks}}, 
                qtype="album,track"
            )
            artist_info.update({
                'top_tracks': parsed_info['tracks'],
                'albums': parsed_info['albums']
            })
            return artist_info
        elif qtype == 'playlist':
            if self.username is None:
                self.set_username()
            playlist = self.sp.playlist(item_id)
            return parsers.parse_playlist(playlist, self.username, detailed=True)
        else:
            raise ValueError(f"Unknown qtype: {qtype}")

    # ---- Playback methods ----

    def get_current_track(self) -> Optional[Dict]:
        """Get information about the currently playing track."""
        try:
            current = self.sp.current_user_playing_track()
            if not current or current.get('currently_playing_type') != 'track':
                return None

            track_info = parsers.parse_track(current['item'])
            track_info['is_playing'] = current.get('is_playing', False)
            return track_info
        except Exception as e:
            self.logger.error(f"Error getting current track: {e}")
            raise

    def is_track_playing(self) -> bool:
        """Check if a track is actively playing."""
        curr_track = self.get_current_track()
        return curr_track and curr_track.get('is_playing', False)

    @auth_helpers.ensure_auth
    @device_helpers.ensure_active_device
    def start_playback(self, spotify_uri=None, device=None):
        """
        Start playback of a Spotify URI.
        
        Args:
            spotify_uri: URI to play ('spotify:track:xxxxx' or 'spotify:album:xxxxx'). 
                        If None, resumes current playback.
            device: Device to play on (will be auto-selected if not provided)
        """
        if not spotify_uri:
            if self.is_track_playing():
                return
            if not self.get_current_track():
                raise ValueError("No track to resume playback.")

        # Determine if URI is a track or a context (album/playlist)
        uris = [spotify_uri] if spotify_uri and spotify_uri.startswith('spotify:track:') else None
        context_uri = spotify_uri if spotify_uri and not uris else None
        device_id = device_helpers.get_device_id(device)

        self.sp.start_playback(uris=uris, context_uri=context_uri, device_id=device_id)

    @auth_helpers.ensure_auth
    @device_helpers.ensure_active_device
    def pause_playback(self, device=None):
        """Pause playback."""
        playback = self.sp.current_playback()
        if playback and playback.get('is_playing'):
            self.sp.pause_playback(device_helpers.get_device_id(device))

    @auth_helpers.ensure_auth
    @device_helpers.ensure_active_device
    def add_to_queue(self, track_id: str, device=None):
        """Add track to queue."""
        self.sp.add_to_queue(track_id, device_helpers.get_device_id(device))

    @auth_helpers.ensure_auth
    @device_helpers.ensure_active_device
    def get_queue(self, device=None):
        """Get the current queue of tracks."""
        queue_info = self.sp.queue()
        queue_info['currently_playing'] = self.get_current_track()
        queue_info['queue'] = [parsers.parse_track(track) for track in queue_info.pop('queue')]
        return queue_info

    def skip_track(self, n=1):
        """Skip n tracks forward."""
        for _ in range(n):
            self.sp.next_track()

    def previous_track(self):
        """Go to previous track."""
        self.sp.previous_track()

    def seek_to_position(self, position_ms):
        """Seek to position in current track."""
        self.sp.seek_track(position_ms=position_ms)

    def set_volume(self, volume_percent):
        """Set playback volume (0-100)."""
        self.sp.volume(volume_percent)

    # ---- Playlist methods ----

    def get_current_user_playlists(self, limit=50) -> List[Dict]:
        """Get current user's playlists."""
        playlists = self.sp.current_user_playlists()
        if not playlists:
            raise ValueError("No playlists found.")
        return [parsers.parse_playlist(p, self.username) for p in playlists['items']]
    
    @auth_helpers.ensure_username
    def get_playlist_tracks(self, playlist_id: str, limit=50) -> List[Dict]:
        """Get tracks from a playlist."""
        playlist = self.sp.playlist(playlist_id)
        if not playlist:
            raise ValueError("No playlist found.")
        return parsers.parse_tracks(playlist['tracks']['items'])
    
    @auth_helpers.ensure_username
    def add_tracks_to_playlist(self, playlist_id: str, track_ids: List[str], position: Optional[int] = None):
        """Add tracks to a playlist."""
        if not playlist_id or not track_ids:
            raise ValueError("playlist_id and track_ids are required.")
        
        self.sp.playlist_add_items(playlist_id, track_ids, position=position)
        self.logger.info(f"Added {len(track_ids)} tracks to playlist {playlist_id}")

    @auth_helpers.ensure_username
    def remove_tracks_from_playlist(self, playlist_id: str, track_ids: List[str]):
        """Remove tracks from a playlist."""
        if not playlist_id or not track_ids:
            raise ValueError("playlist_id and track_ids are required.")
        
        self.sp.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)
        self.logger.info(f"Removed {len(track_ids)} tracks from playlist {playlist_id}")

    @auth_helpers.ensure_username
    def create_playlist(self, name: str, description: Optional[str] = None, public: bool = True):
        """Create a new playlist."""
        if not name:
            raise ValueError("Playlist name is required.")
        
        user = self.sp.current_user()
        playlist = self.sp.user_playlist_create(
            user=user['id'],
            name=name,
            public=public,
            description=description
        )
        self.logger.info(f"Created playlist: {name} (ID: {playlist['id']})")
        return parsers.parse_playlist(playlist, self.username, detailed=True)

    @auth_helpers.ensure_username
    def change_playlist_details(self, playlist_id: str, name: Optional[str] = None, description: Optional[str] = None):
        """Change playlist details."""
        if not playlist_id:
            raise ValueError("playlist_id is required.")
        
        self.sp.playlist_change_details(playlist_id, name=name, description=description)
        self.logger.info(f"Updated playlist details for {playlist_id}")

    # ---- Device methods ----

    def get_devices(self) -> List[Dict]:
        """Get all available devices."""
        return self.sp.devices()['devices']

    def is_active_device(self) -> bool:
        """Check if there's an active device."""
        return device_helpers.is_device_active(self.get_devices())

    def _get_candidate_device(self) -> Dict:
        """Get a candidate device for playback."""
        return device_helpers.get_candidate_device(self.get_devices())
