import discord
import re
import random
from discord.ext.commands import Bot
from discord.ext import commands
class Assign(commands.Cog):
    def __init__(self, client):
        self.client = client
        #--
        @client.command(name="assign")
        async def assign(context):
            if context.author.guild_permissions.administrator or qotdmanager in context.author.roles:
                await context.message.add_reaction(u'\U0001f504')
                x = client.get_emoji(689001238141861934)
                check = client.get_emoji(688998780900737096)
                qotdmanager = context.guild.get_role(674100065043873832)
                staff = context.guild.get_role(564649798196658186)
                excluded = context.guild.get_role(675395764599652362)
                tempexcluded = context.guild.get_role(675452262939885568)
                suspended = context.guild.get_role(676281863605583906)
                staffannouncements = client.get_channel(656636514691973139)
                stafflist = []
                qotdlist = []
                for member in context.guild.members:
                    if staff in member.roles:
                        if tempexcluded in member.roles:
                            await member.remove_roles(tempexcluded)
                        elif excluded in member.roles or suspended in member.roles:
                            pass
                        else:
                            stafflist.append(member)
                #checks for dupes
                for i in range(7):
                    tempchoice = random.choice(stafflist)
                    qotdlist.append(tempchoice)
                    stafflist.remove(tempchoice)
                    await tempchoice.add_roles(tempexcluded)
                embed = discord.Embed(title="QOTD assignments", color=0x8100c2)
                embed.add_field(name="Monday", value=qotdlist[0].mention, inline=False)
                embed.add_field(name="Tuesday", value=qotdlist[1].mention, inline=False)
                embed.add_field(name="Wednesday", value=qotdlist[2].mention, inline=False)
                embed.add_field(name="Thursday", value=qotdlist[3].mention, inline=False)
                embed.add_field(name="Friday", value=qotdlist[4].mention, inline=False)
                embed.add_field(name="Saturday", value=qotdlist[5].mention, inline=False)
                embed.add_field(name="Sunday", value=qotdlist[6].mention, inline=False)
                await staffannouncements.send(embed=embed)
                await context.message.add_reaction(check)
            else:
                await client.say(f"{context.author.mention} {x} Insufficient permissions.")
#run
def setup(client):
    client.add_cog(Assign(client))
