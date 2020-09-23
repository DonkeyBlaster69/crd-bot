import discord
import os
from discord.ext import commands


class Exec(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="exec", aliases=['!'])
    async def exec(self, context, *, command):
        await context.message.add_reaction('\U0001F504')
        if context.author.id == 291661685863874560:
            try:
                exitcode = os.system(f"{command} > output.txt")
                file_object = open("output.txt", "r")
                sayqueue = f"```{file_object.read()}```"
                if sayqueue == '``````':
                    if exitcode == 0:
                        await context.send(f"{self.client.check} Command successfully executed.")
                    elif exitcode == 32512:
                        await context.send(f"```-bash: {command}: command not found```")
                    else:
                        await context.send(f"{self.client.x} Command errored with exit code {exitcode}.")
                else:
                    await context.send(sayqueue)
            except discord.errors.HTTPException as e:
                await context.send(e)
        await context.message.clear_reactions()

    @commands.command(name="upload")
    async def upload(self, context, filepath):
        if context.author.id == 291661685863874560:
            await context.send(file=open(f'{filepath}'))

    @commands.command(name="append")
    async def append(self, context, filepath, *, string):
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


def setup(client):
    client.add_cog(Exec(client))
