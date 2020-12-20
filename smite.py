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
    async def smite(self, context, user: discord.Member = None, operation: str = "smite"):
        if user is None:
            await context.send(f"{context.author.mention} Command usage: `!smite <@user> (grant/deny)`")
        else:
            if operation == "smite":
                c.execute("SELECT smite FROM cheeseballztable WHERE userid=?", (context.author.id,))
                perms = c.fetchone()[0]
                if perms == "True" or context.author.guild_permissions.administrator:
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

            # Granting and denying under this line -----
            elif operation == "grant" or operation == "+" or operation == "allow":
                if context.author.id == 291661685863874560:
                    c.execute("UPDATE cheeseballztable SET smite=True WHERE userid=?", (user.id,))
                    conn.commit()
                    await context.message.add_reaction(self.client.check)
                else:
                    await funcs.noperms(context, self.client)
            elif operation == "revoke" or operation == "-" or operation == "deny":
                if context.author.id == 291661685863874560:
                    c.execute("UPDATE cheeseballztable SET smite=False WHERE userid=?", (user.id,))
                    conn.commit()
                    await context.message.add_reaction(self.client.check)
                else:
                    await funcs.noperms(context, self.client)


def setup(client):
    client.add_cog(Smite(client))
