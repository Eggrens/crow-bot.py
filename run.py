import yaml
import discord
import logging
from discord.ext import commands

from crow.bot import CrowBot

config = None
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

log_handler = logging.FileHandler(filename='crow-bot.log', encoding='utf-8', mode='w')

bot = CrowBot(config)

@bot.event
async def on_ready():
     await bot.load_extension('crow.album_lister')

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

bot.run(log_handler=log_handler)
