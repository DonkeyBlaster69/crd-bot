import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands
class ErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client
        #----------
        @client.event
        async def on_command_error(context, exception):
            
            error = getattr(exception, 'original', exception)
            ignored = (commands.CommandNotFound)
            
            if isinstance(error, commands.CommandOnCooldown):
                await context.send(error)
            else:
                raise error
#run
def setup(client):
    client.add_cog(ErrorHandler(client))
