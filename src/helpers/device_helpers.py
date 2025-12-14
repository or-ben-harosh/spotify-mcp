"""Device management helpers for Spotify client."""

import functools
import logging
from typing import Callable, TypeVar, Optional, Dict, List

logger = logging.getLogger(__name__)

T = TypeVar('T')


def ensure_active_device(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to ensure an active device is available for playback."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not is_device_active(self.get_devices()):
            kwargs['device'] = get_candidate_device(self.get_devices())
        return func(self, *args, **kwargs)
    
    return wrapper


def is_device_active(devices: List[Dict]) -> bool:
    """Check if any device is currently active."""
    return any(device.get('is_active') for device in devices)


def get_candidate_device(devices: List[Dict]) -> Dict:
    """Get a suitable device for playback."""
    if not devices:
        raise ConnectionError("No devices available. Is Spotify open?")
    
    # First, try to find an active device
    for device in devices:
        if device.get('is_active'):
            return device
    
    # If no active device, use the first available one
    logger.info(f"No active device found, using {devices[0]['name']}")
    return devices[0]


def get_device_id(device: Optional[Dict]) -> Optional[str]:
    """Extract device ID from device dict."""
    return device.get('id') if device else None
