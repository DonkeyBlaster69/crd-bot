import discord
import asyncio
import sqlite3
import funcs
from discord.ext import commands
from discord.ext.commands import BucketType

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()


class Smite(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='smite')
    @commands.cooldown(rate=1, per=1, type=BucketType.member)
    async def smite(self, context, user: discord.Member = None):
        if user is None:
            await context.send(f"{context.author.mention} Command usage: `!smite <@user>`")
        else:
            with open('smite.txt') as f:
                if str(context.author.id) in f.read() or context.author.guild_permissions.administrator:
                    if user.id == 291661685863874560:
                        await context.message.add_reaction("\U0001F914")
                        for i in range(10):
                            await asyncio.sleep(0.15)
                            await context.author.send(f"Smited by {context.author}!")
                    else:
                        await context.message.add_reaction(self.client.check)
                        for i in range(10):
                            await asyncio.sleep(0.15)
                            await user.send(f"Smited by {context.author}!")
                else:
                    await funcs.noperms(context, self.client)

    @commands.command(name='addsmite', aliases=['grantsmite'])
    async def addsmite(self, context, user: discord.User = None):
        if user is None:
            await context.send(f"{context.author.mention} Command usage: `!addsmite <@user>`")
        else:
            c.execute("UPDATE cheeseballztable SET smite=True WHERE userid=?", (user.id,))
            await context.message.add_reaction(self.client.check)


def setup(client):
    client.add_cog(Smite(client))
