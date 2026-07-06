import logging
import os
import discord
from discord.ext import commands

class CrowBot(commands.Bot):
    def __init__(self, config, *args, **kwargs): 
        intents = discord.Intents.default()
        intents.presences = False
        intents.typing = False
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix=config['prefix'], intents=intents)

        self.owner_ids = set(config['owners'])
        self.channels = set(config['channels'])
        self.albums = config['albums']
        self.token = config['token']

        for collection in config['collections']:
            folders = [ f for f in os.scandir(collection) if f.is_dir() ]
            for f in folders:
                self.albums.append({ 'name': f.name, 'path': f.path })

        self.albums.sort(key=lambda a: a['name'])

    def run(self, *args, **kwargs):
        super().run(self.token, *args, **kwargs)

