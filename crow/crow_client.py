import discord
import random
from .song import Song

class SongSource(discord.FFmpegOpusAudio):
    def __init__(self, source):
        self.played = 0     # in ms
        super().__init__(source)

    def read(self):
        self.played += 20
        return super().read()

    def elapsed_time(self):
        # return elapsed time as seconds
        return self.played // 1000


class CrowClient(discord.VoiceClient):
    def __init__(self, *args, **kwargs):
        self.queue = []
        self.bot = None
        self.current_song = None
        self.current_source = None
        super().__init__(*args, **kwargs)

    def track_done(self, error):
        if self.queue:
            # play next song in queue
            next_song = self.queue.pop(0)
            next_source = SongSource(next_song.path)
            self.current_song = next_song
            self.current_source = next_source
            self.play(next_source, after=self.track_done)
            self.bot.dispatch("crow_song", str(next_song))
        else:
            self.current_song = None
            self.current_source = None
            self.bot.dispatch("crow_done", self)

    def add_to_queue(self, song: Song, bot):
        if not self.bot:
            self.bot = bot

        # add song to the queue if it has songs, else start playing it immediately
        if self.queue or self.is_playing():
            self.queue.append(song)
        else:
            self.current_song = song
            source = SongSource(song.path)
            self.current_source = source
            self.play(source, after=self.track_done)
            self.bot.dispatch("crow_song", str(song))

    def skip_song(self, index=0):
        # skip current song and play the one at the index specified, removing any songs before it
        if self.is_playing():
            if index > 0:
                # remove songs from queue up to the index
                self.queue = self.queue[index:]

            self.stop()

    def playtime(self):
        # return current elapsed time of song (xx:xx/yy:yy)
        song_time = self.current_song.formatted_time()
        current_elapsed = self.current_source.elapsed_time()

        elapsed_hours = current_elapsed // 3600
        elapsed_minutes = (current_elapsed // 60) % 60
        elapsed_seconds = current_elapsed % 60

        if elapsed_hours < 1:
            current_time = f"{elapsed_minutes}:{elapsed_seconds:02d}"
        else:
            current_time = f"{elapsed_hours}:{elapsed_minutes:02d}:{elapsed_seconds:02d}"

        return f"{current_time} / {song_time}"

    def clear_queue(self):
        self.queue = []

    def shuffle_queue(self):
        random.shuffle(self.queue)

