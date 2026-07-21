import discord
from .song import Song
from .listing import list_ls_format, list_songs_format, get_songs_from_album, get_album
from discord.ext import commands

class AlbumLister(commands.Cog, name='Album-related'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            help='list all available albums defined in the config'
    )
    async def albums(self, ctx):
        album_list = [ a['name'] for a in self.bot.albums ]
        await list_ls_format("albums", album_list, ctx)

    @commands.command(
        help='list all songs in a given album. add "-n" to display songs in a numbered list, or "-t" to also display song metadata (title & artist)',
        usage='<album name> [-n or -t]'
    )
    async def list(self, ctx, album_title, arg=None):
        numbered = (arg == '-n')
        numbered_with_titles = (arg == '-t')
        album = get_album(album_title, self.bot.albums)

        if not album:
            await ctx.send(f"album {album_title} not found!")
            return

        songs = get_songs_from_album(album['path'])

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
