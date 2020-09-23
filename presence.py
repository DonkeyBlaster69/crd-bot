import discord
from discord.ext import commands


class Presence(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='presence')
    async def presence(self, context, presencetype: str = None, content: str = None):
        if presencetype is None:
            await context.send(f"{context.author.mention} Command usage: `!presence <playing/watching/listening/reset> <content>`")
        else:
            staff = context.guild.get_role(564649798196658186)
            if staff in context.author.roles or context.author.guild_permissions.administrator:
                async def logpresence(typechosen, message):
                    embed = discord.Embed(title="Bot Presence Modified", color=0xc6c6c6)
                    embed.add_field(name="User", value=context.author.mention, inline=True)
                    embed.add_field(name="Type", value=typechosen, inline=True)
                    embed.add_field(name="Content", value=message, inline=False)
                    await self.client.logs.send(embed=embed)

                if presencetype == "playing":
                    await self.client.change_presence(activity=discord.Game(content))
                    await context.message.add_reaction(self.client.check)
                    await logpresence("Playing", content)

                elif presencetype == "watching":
                    await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=content))
                    await context.message.add_reaction(self.client.check)
                    await logpresence("Watching", content)

                elif presencetype == "listening":
                    await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=content))
                    await context.message.add_reaction(self.client.check)
                    await logpresence("Listening", content)

                elif presencetype == "reset":
                    await self.client.change_presence(activity=discord.Game(""))
                    await context.message.add_reaction(self.client.check)
                    embed = discord.Embed(title="Bot Presence Reset", color=0xc6c6c6)
                    embed.add_field(name="User", value=context.author.mention, inline=True)
                    await self.client.logs.send(embed=embed)

                else:
                    await context.send(f"{context.author.mention} Command usage: `!presence <playing/watching/listening/reset> <content>`")
            else:
                await context.send(f"{context.author.mention} {self.client.x} Insufficient permissions.")


def setup(client):
    client.add_cog(Presence(client))
