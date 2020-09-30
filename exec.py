import discord
import os
from discord.ext import commands


class Exec(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="exec", aliases=['!'])
    @commands.is_owner()
    async def exec(self, context, *, command):
        await context.message.add_reaction('\U0001F504')
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
    @commands.is_owner()
    async def upload(self, context, filepath):
        await context.send(file=open(f'{filepath}'))

    @commands.command(name="append")
    @commands.is_owner()
    async def append(self, context, filepath, *, string):
        try:
            exitcode = os.system(f'echo "{string}" | tee -a {filepath} >/dev/null > output.txt')
            if exitcode == 0:
                await context.send(f"{self.client.check} Appended `{string}` to {filepath}.")
            else:
                await context.send(f"{self.client.x} Command errored with exit code {exitcode}.")
        except discord.errors.HTTPException as e:
            await context.send(e)


def setup(client):
    client.add_cog(Exec(client))
