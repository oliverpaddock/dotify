"""A collection of models corresponding to different Spotify entities."""

__all__ = [
    "Album",
    "Artist",
    "Image",
    "Playlist",
    "Track",
    "User",
]

import time

start=time.time()
from dotify.models._album import Album
end=time.time()
print('30', end-start)
start=end
from dotify.models._artist import Artist
end=time.time()
print('31', end-start)
start=end
from dotify.models._image import Image
end=time.time()
print('32', end-start)
start=end
from dotify.models._playlist import Playlist
end=time.time()
print('33', end-start)
start=end
from dotify.models._track import Track
end=time.time()
print('34', end-start)
start=end
from dotify.models._user import User
end=time.time()
print('35', end-start)
start=end