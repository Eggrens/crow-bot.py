import discord
import os
import io
import random
from .listing import list_songs_format, get_songs_from_album, get_album
from .song import Song
from .crow_client import CrowClient
from discord.ext import commands

class Player(commands.Cog, name='Player'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        help="shows what song is currently playing",
        aliases=['np']
    )
    async def nowplaying(self, ctx):
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
        help="shows a list of the songs currently in the queue",
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
        help="add a song to the queue (search by filepath)",
        aliases=['p'],
        usage='<filepath>'
    )
    async def play(self, ctx, file):
        if not os.path.isfile(file):
            await ctx.send(f"**{file}** was not found, or is not a file")
            return
            
        song = Song(file)
        ctx.voice_client.add_to_queue(song, self.bot)
        await ctx.send(f"caw! added **{song}** (`{song.formatted_time()}`) to the queue")

    @commands.command(
        help="adds all songs in the album to the queue. add '-s' to shuffle before inserting.",
        aliases=['pa'],
        usage="<album name> [-s]"
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
        help="adds a song from an album with the given track number/index to the queue. use `~list <album name> -n` to get the index numbers of songs in the album",
        aliases=['pt'],
        usage="<album name> <index>"
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
        help="resumes playback"
    )
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("caw! resumed playback")
        else:
            await ctx.send("i'm already playing...")

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
        help="skips to the next track in the queue. add an index number to skip to a specific song in the queue",
        usage="[index]"
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
