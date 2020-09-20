import discord
import os
from discord.ext.commands import Bot
from discord.ext import commands
class Exec(commands.Cog):
    def __init__(self, client):
        self.client = client
        #----------
        @client.command(name="exec",
                        aliases=['!'])
        async def exec(context,*,command):
            await context.message.add_reaction('\U0001F504')
            check = discord.utils.get(context.guild.emojis, name="checkmark")
            x = discord.utils.get(context.guild.emojis, name="xmark")
            if context.author.id == 291661685863874560:
                try:
                    exitcode = os.system(f"{command} > output.txt")
                    file_object = open("output.txt","r")
                    sayqueue = f"```{file_object.read()}```"
                    if sayqueue == ('``````'):
                        if exitcode == 0:
                            await context.send(f"{check} Command successfully executed.")
                        elif exitcode == 32512:
                            await context.send(f"```-bash: {command}: command not found```")
                        else:
                            await context.send(f"{x} Command errored with exit code {exitcode}.")
                    else:
                        await context.send(sayqueue)
                except discord.errors.HTTPException as e:
                    await context.send(e)
            await context.message.clear_reactions()
        #upload
        @client.command(name="upload")
        async def upload(context,*,filepath):
            if context.author.id == 291661685863874560:
                await context.send(file = open(f'{filepath}'))
        #append
        @client.command(name="append")
        async def append(context,filepath,*,string):
            x = discord.utils.get(context.guild.emojis, name="xmark")
            check = discord.utils.get(context.guild.emojis, name="checkmark")
            if context.author.id == 291661685863874560:
                try:
                    exitcode = os.system(f'echo "{string}" | tee -a {filepath} >/dev/null > output.txt')
                    if exitcode == 0:
                        await context.send(f"{check} Appended `{string}` to {filepath}.")
                    else:
                        await context.send(f"{x} Command errored with exit code {exitcode}.")
                except discord.errors.HTTPException as e:
                    await context.send(e)
#run
def setup(client):
    client.add_cog(Exec(client))
