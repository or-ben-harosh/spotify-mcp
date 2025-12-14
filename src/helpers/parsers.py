"""Parsing utilities for Spotify API responses."""

from collections import defaultdict
from typing import Optional, Dict, List


def parse_track(track_item: dict, detailed: bool = False) -> Optional[dict]:
    """Parse a track item from Spotify API."""
    if not track_item:
        return None
    
    narrowed_item = {
        'name': track_item['name'],
        'id': track_item['id'],
    }

    if 'is_playing' in track_item:
        narrowed_item['is_playing'] = track_item['is_playing']

    if detailed:
        narrowed_item['album'] = parse_album(track_item.get('album'))
        narrowed_item['track_number'] = track_item.get('track_number')
        narrowed_item['duration_ms'] = track_item.get('duration_ms')

    if not track_item.get('is_playable', True):
        narrowed_item['is_playable'] = False

    artists = [a['name'] for a in track_item['artists']]
    if detailed:
        artists = [parse_artist(a) for a in track_item['artists']]

    narrowed_item['artist' if len(artists) == 1 else 'artists'] = artists[0] if len(artists) == 1 else artists

    return narrowed_item


def parse_artist(artist_item: dict, detailed: bool = False) -> Optional[dict]:
    """Parse an artist item from Spotify API."""
    if not artist_item:
        return None
    
    narrowed_item = {
        'name': artist_item['name'],
        'id': artist_item['id'],
    }
    
    if detailed:
        narrowed_item['genres'] = artist_item.get('genres')

    return narrowed_item


def parse_playlist(playlist_item: dict, username: str, detailed: bool = False) -> Optional[dict]:
    """Parse a playlist item from Spotify API."""
    if not playlist_item:
        return None
    
    narrowed_item = {
        'name': playlist_item['name'],
        'id': playlist_item['id'],
        'owner': playlist_item['owner']['display_name'],
        'user_is_owner': playlist_item['owner']['display_name'] == username,
        'total_tracks': playlist_item['tracks']['total'],
    }
    
    if detailed:
        narrowed_item['description'] = playlist_item.get('description')
        narrowed_item['tracks'] = [
            parse_track(t['track']) for t in playlist_item['tracks']['items']
        ]

    return narrowed_item


def parse_album(album_item: dict, detailed: bool = False) -> dict:
    """Parse an album item from Spotify API."""
    narrowed_item = {
        'name': album_item['name'],
        'id': album_item['id'],
    }

    artists = [a['name'] for a in album_item['artists']]

    if detailed:
        narrowed_item["tracks"] = [parse_track(t) for t in album_item['tracks']['items']]
        artists = [parse_artist(a) for a in album_item['artists']]
        for key in ['total_tracks', 'release_date', 'genres']:
            narrowed_item[key] = album_item.get(key)

    narrowed_item['artist' if len(artists) == 1 else 'artists'] = artists[0] if len(artists) == 1 else artists

    return narrowed_item


def parse_search_results(results: Dict, qtype: str, username: Optional[str] = None) -> Dict:
    """Parse search results from Spotify API."""
    _results = defaultdict(list)

    for q in qtype.split(","):
        if q == "track":
            _results['tracks'] = [parse_track(item) for item in results['tracks']['items'] if item]
        elif q == "artist":
            _results['artists'] = [parse_artist(item) for item in results['artists']['items'] if item]
        elif q == "playlist":
            _results['playlists'] = [parse_playlist(item, username) for item in results['playlists']['items'] if item]
        elif q == "album":
            _results['albums'] = [parse_album(item) for item in results['albums']['items'] if item]
        else:
            raise ValueError(f"Unknown qtype: {q}")

    return dict(_results)


def parse_tracks(items: List[Dict]) -> List[Dict]:
    """Parse a list of track items."""
    return [parse_track(item['track']) for item in items if item]
