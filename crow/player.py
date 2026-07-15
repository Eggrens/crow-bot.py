import discord
import os
import io
import random
from .listing import list_songs_format, get_songs_from_album, get_album
from .song import Song
from discord.ext import commands

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


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        help="shows what's currently playing",
        aliases=['np']
    )
    async def nowplaying(self, ctx):
        # TODO: replace with an embed
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("i'm not playing anything!!")
            return

        song = ctx.voice_client.current_song
        song_cover = None

        embed = discord.Embed(
            title="Playing:",
            description=f"`{ctx.voice_client.playtime()}`",
            color=discord.Colour.dark_purple()
        )
        
        if song.title:
            embed.add_field(name="Title", value=song.title, inline=False)
        else:
            embed.add_field(name="Filename", value=song.filename, inline=False)

        if song.artist:
            embed.add_field(name="Artist", value=song.artist, inline=False)

        if song.album:
            embed.add_field(name="Album", value=song.album, inline=False)

        if song.image:
            song_cover = discord.File(io.BytesIO(song.image.data), filename="cover.png")
            embed.set_thumbnail(url="attachment://cover.png")

        await ctx.send(file=song_cover, embed=embed)

    @commands.command(
        help="shows what's in the queue",
        aliases=['q']
    )
    async def queue(self, ctx):
        if not ctx.voice_client:
            await ctx.send("i'm not playing anything!!")
            return

        if not ctx.voice_client.queue:
            await ctx.send("caw! queue is empty")
        else:
            await list_songs_format("queue", ctx.voice_client.queue, False, ctx) 

    @commands.command(
        help="adds a song file (given a filepath) to the queue, or resumes playback",
        aliases=['p']
    )
    async def play(self, ctx, file=None):
        if not file:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                await ctx.send("caw! resumed playback")
            else:
                await ctx.send("i'm already playing...")
            return

        if not os.path.isfile(file):
            await ctx.send(f"**{file}** was not found, or is not a file")
            return
            
        song = Song(file)
        ctx.voice_client.add_to_queue(song, self.bot)
        await ctx.send(f"caw! added **{song}** (`{song.formatted_time()}`) to the queue")

    @commands.command(
        help="adds all songs in the album to the queue. add '-s' to the end to shuffle before inserting.",
        aliases=['pa']
    )
    async def playalbum(self, ctx, album, shuffle=None):
        album_to_play = get_album(album, self.bot.albums)

        if not album_to_play:
            await ctx.send(f"album **{album}** was not found... did you set the config right?")
            return

        songs = get_songs_from_album(album_to_play['path'])

        if not songs:
            await ctx.send(f"album **{album}** has no songs in it!")
            return

        if shuffle == "-s":
            random.shuffle(songs)

        for song in songs:
            ctx.voice_client.add_to_queue(song, self.bot)

        await ctx.send(f"caw! added **{len(songs)}** songs from **{album}** to the queue") 

    @commands.command(
        help="adds a song from an album with the given track number/index to the queue.",
        aliases=['pt']
    )
    async def playtrack(self, ctx, album, index: int):
        album_to_search = get_album(album, self.bot.albums)

        if not album_to_search:
            await ctx.send(f"album **{album}** was not found... did you set the config right?")
            return

        songs = get_songs_from_album(album_to_search['path'])

        if not songs:
            await ctx.send(f"album **{album}** has no songs in it!")
            return

        if index < 1 or index > len(songs):
            await ctx.send(f"invalid song number given. album **{album}** has **{len(songs)}** songs in it")
            return

        ctx.voice_client.add_to_queue(songs[index-1], self.bot)
        await ctx.send(f"caw! added **{songs[index-1]}** from **{album}** to the queue.")

    @commands.command(
        help="pauses playback"
    )
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("caw! paused")
        else:
            await ctx.send("but i'm not playing anything...")

    @commands.command(
        help="disconnect crow from the voice channel and clear the queue"
    )
    async def stop(self, ctx):
        if not ctx.voice_client:
            await ctx.send("but i'm not playing anything...")
            return

        ctx.voice_client.clear_queue()
        await ctx.voice_client.disconnect()

    @commands.command(
        help="shuffles the queue"
    )
    async def shuffle(self, ctx):
        if not ctx.voice_client:
            await ctx.send("but i'm not playing anything...")
            return

        if not ctx.voice_client.queue:
            await ctx.send("i've got nothing in my queue to shuffle!")
            return

        ctx.voice_client.shuffle_queue()
        await ctx.send("caw! shuffling queue")

    @commands.command(
        help="skips to the next track in the queue. add an index number to skip to a specific song in the queue"
    )
    async def skip(self, ctx, index: int = 1):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("i'm not playing anything!!")
            return

        if ctx.voice_client.queue:
            if index < 1 or index > len(ctx.voice_client.queue):
                await ctx.send("invalid queue position")
                return

            song_to_play = ctx.voice_client.queue[index-1]
            await ctx.send(f"skipping to **{song_to_play}**")
            ctx.voice_client.skip_song(index-1)
        else:
            await ctx.send("no more songs left, ending playback")
            ctx.voice_client.skip_song()

    @play.before_invoke
    @playalbum.before_invoke
    @playtrack.before_invoke
    async def connect_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(cls=CrowClient)
            else:
                await ctx.send("caw! you're not in a voice channel, please connect to one")

async def setup(bot):
    await bot.add_cog(Player(bot))
