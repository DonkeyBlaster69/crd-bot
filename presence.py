import discord
import time
from discord.ext.commands import Bot
from discord.ext import commands
class Presence(commands.Cog):
    def __init__(self, client):
        self.client = client
        #definitions
        check = client.get_emoji(688998780900737096)
        x = client.get_emoji(689001238141861934)
        logs = client.get_channel(657112105467772929)
        #presence
        @client.command(name='presence')
        async def presence(context, presencetype:str=None, content:str=None):
            if presencetype == None:
                await context.send(f"{context.author.mention} Command usage: `!presence <playing/watching/listening/reset> <content>`")
            else:
                staff = context.guild.get_role(564649798196658186)
                if staff in context.author.roles or context.author.guild_permissions.administrator:
                    async def logpresence(typechosen, message):
                        embed = discord.Embed(title="Bot Presence Modified", color=0xc6c6c6)
                        embed.add_field(name="User", value=context.author.mention, inline=True)
                        embed.add_field(name="Type", value=typechosen, inline=True)
                        embed.add_field(name="Content", value=message, inline=False)
                        await logs.send(embed=embed)
                    if presencetype == "playing":
                        await client.change_presence(activity = discord.Game(content))
                        await context.message.add_reaction(check)
                        await logpresence("Playing", content)
                    elif presencetype == "watching":
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=content))
                        await context.message.add_reaction(check)
                        await logpresence("Watching", content)
                    elif presencetype == "listening":
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=content))
                        await context.message.add_reaction(check)
                        await logpresence("Listening", content)
                    elif presencetype == "reset":
                        await client.change_presence(activity = discord.Game(""))
                        await context.message.add_reaction(check)
                        embed = discord.Embed(title="Bot Presence Reset", color=0xc6c6c6)
                        embed.add_field(name="User", value=context.author.mention, inline=True)
                        await logs.send(embed=embed)
                    else:
                        await context.send(f"{context.author.mention} Command usage: `!presence <playing/watching/listening/reset> <content>`")
                else:
                    await context.send(f"{context.author.mention} {x} Insufficient permissions.") 
    #run
def setup(client):
    client.add_cog(Presence(client))
