import discord
import random
from discord.ext import commands


class Assign(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="assign")
    @commands.has_guild_permissions(administrator=True)
    async def assign(self, context):
        await context.message.add_reaction(u'\U0001f504')
        # Get roles
        staff = context.guild.get_role(564649798196658186)
        excluded = context.guild.get_role(675395764599652362)
        tempexcluded = context.guild.get_role(675452262939885568)
        suspended = context.guild.get_role(676281863605583906)
        # --
        bot = context.guild.get_role(656885049370607644)  # Bot Developer
        assist = context.guild.get_role(750350186877812878)  # Assistant Deputy Director
        deputy = context.guild.get_role(658491821151748155)  # Deputy Director
        director = context.guild.get_role(528682495089180682)  # Community Relations Director
        overseer = context.guild.get_role(528682488613306379)  # Community Relations Overseer

        stafflist = []
        trlist = []
        crdqotdlist = []
        trqotdlist = []
        for member in context.guild.members:
            if excluded not in member.roles and suspended not in member.roles:
                if staff in member.roles:
                    if tempexcluded in member.roles:
                        await member.remove_roles(tempexcluded)
                    else:
                        stafflist.append(member)
            if bot in member.roles or assist in member.roles or deputy in member.roles or director in member.roles or overseer in member.roles:
                print(member)
                trlist.append(member)

        # checks for dupes
        for i in range(7):
            tempchoice1 = random.choice(stafflist)
            crdqotdlist.append(tempchoice1)
            stafflist.remove(tempchoice1)
            await tempchoice1.add_roles(tempexcluded)

            tempchoice2 = random.choice(trlist)
            trqotdlist.append(tempchoice2)
            trlist.remove(tempchoice2)

        embed = discord.Embed(title="QOTD assignments", color=0x8100c2)
        embed.add_field(name="Monday", value=f"CRD: {crdqotdlist[0].mention}\nTR: {trqotdlist[0].mention}", inline=False)
        embed.add_field(name="Tuesday", value=f"CRD: {crdqotdlist[1].mention}\nTR: {trqotdlist[1].mention}", inline=False)
        embed.add_field(name="Wednesday", value=f"CRD: {crdqotdlist[2].mention}\nTR: {trqotdlist[2].mention}", inline=False)
        embed.add_field(name="Thursday", value=f"CRD: {crdqotdlist[3].mention}\nTR: {trqotdlist[3].mention}", inline=False)
        embed.add_field(name="Friday", value=f"CRD: {crdqotdlist[4].mention}\nTR: {trqotdlist[4].mention}", inline=False)
        embed.add_field(name="Saturday", value=f"CRD: {crdqotdlist[5].mention}\nTR: {trqotdlist[5].mention}", inline=False)
        embed.add_field(name="Sunday", value=f"CRD: {crdqotdlist[6].mention}\nTR: {trqotdlist[6].mention}", inline=False)
        staffannouncements = self.client.get_channel(656636514691973139)
        await staffannouncements.send(embed=embed)
        await context.message.add_reaction(self.client.check)


def setup(client):
    client.add_cog(Assign(client))
