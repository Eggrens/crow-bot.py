import os

from tinytag import TinyTag

class Song:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        tag = TinyTag.get(path, image=True)
        self.title = tag.title
        self.artist = tag.artist
        self.album = tag.album
        self.track = tag.track
        self.disc = tag.disc if tag.disc is not None else 0
        self.duration = int(tag.duration)
        self.image = tag.images.any

    def __str__(self):
        if self.title and self.artist:
            return f"{self.title} - {self.artist}"
        else:
            return self.title if self.title else self.filename

    def formatted_time(self):
        hours = self.duration // 3600
        minutes = (self.duration // 60) % 60
        seconds = self.duration % 60

        if hours < 1:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def has_track_number(self):
        return (self.track is not None)

