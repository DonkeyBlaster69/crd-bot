import discord
import re
import sqlite3
import asyncio
import funcs
from discord.ext import commands

conn = sqlite3.connect('staff.db')
c = conn.cursor()


class Staff(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='staffsql')
    @commands.is_owner()
    async def staffsql(self, context, *, command: str = None):
        if command is None:
            await context.send(f"{context.author.mention} Command usage: `!staffsql <command>`")
        else:
            try:
                c.execute(command)
                await context.send(c.fetchall())
                conn.commit()
            except Exception as e:
                await context.send(e)

    # check for [event] tag
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 656798105957564416:
            starttags = ['[event]', '*[event]*', '**[event]**', '***[event]***', 'https']
            for tag in starttags:
                if tag in message.content.lower():
                    c.execute("SELECT weekevents FROM stafftable WHERE userid=?", (message.author.id,))
                    c.execute("UPDATE stafftable SET weekevents=? WHERE userid=?", (int(c.fetchone()[0]) + 1, message.author.id))
                    c.execute("SELECT totalevents FROM stafftable WHERE userid=?", (message.author.id,))
                    c.execute("UPDATE stafftable SET totalevents=? WHERE userid=?", (int(c.fetchone()[0]) + 1, message.author.id))
                    conn.commit()
                    await message.add_reaction(self.client.check)

    @commands.command(name='resetweek')
    @commands.has_guild_permissions(administrator=True)
    async def resetweek(self, context, user: discord.User = None):
        if user is None:
            c.execute("UPDATE stafftable SET weekevents=0")
            conn.commit()
            await context.message.add_reaction(self.client.check)
        else:
            c.execute("SELECT weekevents FROM stafftable WHERE userid=?", (user.id,))
            weekevents = c.fetchone()[0]
            c.execute("UPDATE stafftable SET weekevents=0 WHERE userid=?", (user.id,))
            conn.commit()
            await context.send(f"{context.author.mention} Cleared events for {user.mention}, they had {weekevents} events.")

    @commands.command(name='clearevents')
    async def clearevents(self, context):
        allowedIDs = [475514947472982026, 291661685863874560, 358757337751748609]
        # nscheese, myself, omega
        if context.author.id in allowedIDs:
            await context.send(f"{context.author.mention} Are you sure you want to clear the ENTIRE database? [yes]")

            def check(m):
                return m.author.id == context.author.id and m.channel == context.channel

            try:
                reply = await self.client.wait_for('message', check=check, timeout=20)
                if reply.content == 'yes':
                    c.execute("UPDATE stafftable SET weekevents=0")
                    c.execute("UPDATE stafftable SET totalevents=0")
                    conn.commit()
                    await context.message.add_reaction(check)
                else:
                    raise asyncio.TimeoutError
            except asyncio.TimeoutError:
                await context.send(f"{context.author.mention} Timed out or cancelled.")
        else:
            await context.send(f"{context.author.mention} {self.client.x} Insufficient permissions.")

    @commands.command(name='events')
    async def events(self, context, user: discord.Member = None, action: str = 'view', amount: int = None):
        probsupervisor = context.guild.get_role(712885985897218059)
        advisory = context.guild.get_role(658491826096832513)
        if action == 'view':
            async def fetch(staff):
                c.execute("SELECT weekevents FROM stafftable WHERE userid=?", (staff.id,))
                weekevents = re.sub("[(),\[\]]", "", str(c.fetchall()))
                if weekevents == '':
                    await context.send(f"{context.author.mention} Specified staff member not found.")
                else:
                    c.execute("SELECT totalevents FROM stafftable WHERE userid=?", (staff.id,))
                    totalevents = re.sub("[(),\[\]]", "", str(c.fetchall()))
                    embed = discord.Embed(title="", color=0x800080)
                    embed.set_author(name=staff, icon_url=staff.avatar_url)
                    embed.add_field(name="Staff member", value=staff.mention, inline=True)
                    embed.add_field(name="Events this week", value=weekevents, inline=True)
                    embed.add_field(name="Total events", value=totalevents, inline=True)
                    await context.send(embed=embed)

            if user is None:
                await fetch(context.author)
            else:
                await fetch(user)
        if context.author.guild_permissions.administrator or probsupervisor in context.author.roles or advisory in context.author.roles:
            if action == '+' or action == 'add':
                if amount is None:
                    await context.send(f"{context.author.mention} Command usage: `!events <@user> <view/+/-> <amount>`")
                else:
                    c.execute("SELECT totalevents FROM stafftable WHERE userid=?", (user.id,))
                    totalevents = int(c.fetchone()[0])
                    c.execute("UPDATE stafftable SET totalevents=? WHERE userid=?", (totalevents + amount, user.id))
                    await context.message.add_reaction(self.client.check)
            elif action == '-' or action == 'remove':
                if amount is None:
                    await context.send(f"{context.author.mention} Command usage: `!events <@user> <view/+/-> <amount>`")
                else:
                    c.execute("SELECT totalevents FROM stafftable WHERE userid=?", (user.id,))
                    totalevents = int(c.fetchone()[0])
                    c.execute("UPDATE stafftable SET totalevents=? WHERE userid=?", (totalevents - amount, user.id))
                    await context.message.add_reaction(self.client.check)
            elif action == 'view':
                pass
            else:
                await context.send(f"{context.author.mention} Command usage: `!events <@user> <view/+/-> <amount>`")
            conn.commit()
        else:
            if action != 'view':
                await funcs.noperms(context, self.client)

    @commands.command(name='addstaff')
    async def addstaff(self, context, staff: discord.Member = None):
        supervisor = context.guild.get_role(712885985897218059)
        if staff is None:
            await context.send(f"{context.author.mention} Command usage: `!addstaff <@staff member>`")
        else:
            if context.author.guild_permissions.administrator or supervisor in context.author.roles:
                c.execute("DELETE FROM stafftable WHERE userid=?", (staff.id,))
                c.execute("INSERT INTO stafftable(userid, weekevents, totalevents) VALUES (?, 0, 0)", (staff.id,))
                conn.commit()
                await context.message.add_reaction(self.client.check)
            else:
                await context.send(f"{context.author.mention} {self.client.x} Insufficient permissions.")

    @commands.command(name='staff')
    async def staff(self, context):
        # parse roles into objects--------------------------------------------
        pending = context.guild.get_role(658491829821374505)
        probationary = context.guild.get_role(658491829431566347)
        manager = context.guild.get_role(658491828433059844)
        senior = context.guild.get_role(658491828106035210)
        chief = context.guild.get_role(658491827652919296)
        advisory = context.guild.get_role(658491826096832513)
        head = context.guild.get_role(717224729236209743)
        executive = context.guild.get_role(658491825602035742)
        bot = context.guild.get_role(656885049370607644)
        assist = context.guild.get_role(750350186877812878)
        deputy = context.guild.get_role(658491821151748155)
        director = context.guild.get_role(528682495089180682)
        overseer = context.guild.get_role(528682488613306379)
        # empty lists to parse members----------------------------------------
        pendingList = []
        probationaryList = []
        managerList = []
        seniorList = []
        chiefList = []
        headList = []
        advisoryList = []
        executiveList = []
        botList = []
        assistList = []
        deputyList = []
        directorList = []
        overseerList = []
        # return member objects and parse into lists--------------------------
        for member in context.guild.members:
            c.execute("SELECT weekevents FROM stafftable WHERE userid=?", (member.id,))
            weekevents = re.sub("[()',\[\]]", "", str(c.fetchall()))
            if pending in member.roles:
                pendingList.append(f" - {member.mention}: {weekevents}")
            if probationary in member.roles:
                probationaryList.append(f" - {member.mention}: {weekevents}")
            if manager in member.roles:
                managerList.append(f" - {member.mention}: {weekevents}")
            if senior in member.roles:
                seniorList.append(f" - {member.mention}: {weekevents}")
            if chief in member.roles:
                chiefList.append(f" - {member.mention}: {weekevents}")
            if head in member.roles:
                headList.append(f" - {member.mention}: {weekevents}")
            if advisory in member.roles:
                advisoryList.append(f" - {member.mention}: {weekevents}")
            if executive in member.roles:
                executiveList.append(f" - {member.mention}: {weekevents}")
            if bot in member.roles:
                botList.append(f" - {member.mention}: {weekevents}")
            if assist in member.roles:
                assistList.append(f" - {member.mention}: {weekevents}")
            if deputy in member.roles:
                deputyList.append(f" - {member.mention}: {weekevents}")
            if director in member.roles:
                directorList.append(f" - {member.mention}: {weekevents}")
            if overseer in member.roles:
                overseerList.append(f" - {member.mention}: {weekevents}")
        # logic for empty lists
        if overseerList == []:
            overseerMessage = "Apparently we don't have an overseer at the moment."
        else:
            overseerMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(overseerList)))
        if directorList == []:
            directorMessage = "Apparently we don't have a director at the moment."
        else:
            directorMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(directorList)))
        if deputyList == []:
            deputyMessage = "Currently no Deputy Directors."
        else:
            deputyMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(deputyList)))
        if assistList == []:
            assistMessage = "Currently no Assistant Deputy Directors."
        else:
            assistMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(assistList)))
        if executiveList == []:
            executiveMessage = "Currently no Executive Managers."
        else:
            executiveMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(executiveList)))
        if advisoryList == []:
            advisoryMessage = "Currently no Advisory Boards."
        else:
            advisoryMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(advisoryList)))
        if headList == []:
            headMessage = "Currently no Head Mangers."
        else:
            headMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(headList)))
        if chiefList == []:
            chiefMessage = "Currently no Chief Managers."
        else:
            chiefMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(chiefList)))
        if seniorList == []:
            seniorMessage = "Currently no Senior Managers."
        else:
            seniorMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(seniorList)))
        if managerList == []:
            managerMessage = "Currently no Managers."
        else:
            managerMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(managerList)))
        if probationaryList == []:
            probationaryMessage = "Currently no Probationary Managers."
        else:
            probationaryMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(probationaryList)))
        if pendingList == []:
            pendingMessage = "Currently no Pending Managers."
        else:
            pendingMessage = re.sub("[,]", "\n", re.sub("[()'\[\]]", "", str(pendingList)))
        # move into embed and send -----------------------------------------------
        embed = discord.Embed(title="Current Staff List", color=0x8100c2)
        embed.add_field(name="Overseer", value=overseerMessage, inline=False)
        embed.add_field(name="Director", value=directorMessage, inline=False)
        embed.add_field(name="Deputy Director", value=deputyMessage, inline=False)
        embed.add_field(name="Assistant Deputy Director", value=assistMessage, inline=False)
        embed.add_field(name="Bot Developer", value=re.sub("[()'\[\]]", "", str(botList)), inline=False)
        embed.add_field(name="Executive Manager", value=executiveMessage, inline=False)
        embed.add_field(name="Advisory Board", value=advisoryMessage, inline=False)
        embed.add_field(name="Head Manager", value=headMessage, inline=False)
        embed.add_field(name="Chief Manager", value=chiefMessage, inline=False)
        embed.add_field(name="Senior Manager", value=seniorMessage, inline=False)
        embed.add_field(name="Manager", value=managerMessage, inline=False)
        embed.add_field(name="Probationary Manager", value=probationaryMessage, inline=False)
        embed.add_field(name="Pending Manager", value=pendingMessage, inline=False)
        await context.send(embed=embed)


def setup(client):
    client.add_cog(Staff(client))
