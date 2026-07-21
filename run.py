import yaml
import discord
import logging
from discord.ext import commands

from crow.bot import CrowBot

config = None
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

starting_activity = discord.CustomActivity(name=f"Type {config['prefix']}help for commands")
bot = CrowBot(config, activity=starting_activity, help_command=commands.MinimalHelpCommand())

@bot.event
async def on_ready():
     await bot.load_extension('crow.album_lister')
     await bot.load_extension('crow.player')

@bot.event
async def on_crow_song(song_name):
    activity = discord.Activity(type=discord.ActivityType.listening, name=song_name)
    await bot.change_presence(activity=activity)

@bot.event
async def on_crow_done(voice_client):
    channel = bot.get_channel(bot.status_channel)
    await channel.send("caw! finished playing all my songs")
    await voice_client.disconnect()
    await bot.change_presence(activity=starting_activity)

@bot.command(help='nyon!')
async def nyon(ctx):
    await ctx.send('nyon! :>')

@bot.command(help='caw!')
async def caw(ctx):
    await ctx.send('caw! :>')

@bot.command(help='shut down Crow; owners only')
@commands.is_owner()
async def quit(ctx):
    await ctx.send('caw! shutting down')
    await bot.close()

if config['log']: 
    log_handler = logging.FileHandler(filename='crow-bot.log', encoding='utf-8', mode='w')
    bot.run(log_handler=log_handler)
else:
    bot.run()
