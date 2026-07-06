import discord
import os
from .song import Song
from .listing import list_ls_format, list_songs_format
from discord.ext import commands

class AlbumLister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='list all albums')
    async def albums(self, ctx):
        album_list = [ a['name'] for a in self.bot.albums ]
        await list_ls_format("albums", album_list, ctx)

    @commands.command(
        help='list all songs in a given album. add "-n" to the end to display in a numbered list. add "-t" to display the songs numbered with title + artist'
    )
    async def list(self, ctx, album_title, arg=None):
        numbered = (arg == '-n')
        numbered_with_titles = (arg == '-t')
        album = None
        for a in self.bot.albums:
            if a['name'] == album_title:
                album = a
                break

        if not album:
            await ctx.send(f"album {album_title} not found!")
            return

        songs = []
        for path, dirs, files in os.walk(album['path']):
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext in ['.mp3', '.flac', '.wav']:
                    song = Song(os.path.join(path, filename))
                    songs.append(song)
        songs.sort(key=lambda s: s.filename)

        if songs:
            title = f"songs in {album_title}"
            if numbered:
                await list_songs_format(title, songs, True, ctx)
            elif numbered_with_titles:
                await list_songs_format(title, songs, False, ctx)
            else:
                ls_list = [s.filename for s in songs]
                await list_ls_format(title, ls_list, ctx)
        else:
            await ctx.send(f"album {album_title} has no songs")

async def setup(bot):
    await bot.add_cog(AlbumLister(bot))
