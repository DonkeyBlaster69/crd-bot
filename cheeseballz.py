import discord
import random
import re
import asyncio
from datetime import datetime, timedelta
import sqlite3
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
import main
import cbops

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()


class Cheeseballz(commands.Cog):

    # ---SCHEDULING FOR CLEARING DAILIES
    def __init__(self, client):
        self.client = client

    @tasks.loop(hours=24)
    async def clearCurrentGamble(self):
        c.execute("UPDATE cheeseballztable SET currentgamble=0")
        print("Current gamble reset")
        return
    clearCurrentGamble.start()

    @commands.command(name='cbsql')
    async def cbsql(self, context, *, command: str = None):
        if command is None:
            await context.send(f"{context.author.mention} Command usage: `!cbsql <command>`")
        else:
            if context.author.id == 291661685863874560:
                try:
                    c.execute(command)
                    await context.send(c.fetchall())
                    conn.commit()
                except Exception as e:
                    await context.send(e)
            else:
                await main.noperms(context)

    # event for people joining, making new acc
    @commands.Cog.listener
    async def on_member_join(self, member):
        c.execute("SELECT COUNT(1) FROM cheeseballztable WHERE userid=?", (member.id,))
        if str(c.fetchone()[0]) == '0':
            defaulttime = "2020-01-01 00:00:00.000000"
            c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly, gamblelimit, currentgamble) VALUES (?, 0, 0, ?, ?, ?, 0, 0)", (member.id, defaulttime, defaulttime, defaulttime))
            conn.commit()

    @commands.command(name='cheeseballz', aliases=['cb'])
    async def cheeseballz(self, context, operation: str = None, user: discord.User = None, amount: int = None, *, reason: str = "Not specified"):
        if self.client.cbperms in context.author.roles or context.author.guild_permissions.adminstrator:
            if operation is None or user is None or amount is None:
                await context.send(f"{context.author.mention} Command usage: `!cb <+/-/set> <@user> <amount> <reason>`")
            else:

                def fillembed(embed):
                    embed.add_field(name="Staff", value=context.author.mention, inline=False)
                    embed.add_field(name="User", value=user.mention, inline=True)
                    embed.add_field(name="Amount", value=amount, inline=False)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    return embed

                if operation == "+" or operation == "add":
                    cbops.addcb(user.id, amount)
                    embed = discord.Embed(title="Cheeseballz Added", color=0x00ff00)
                    await self.client.logs.send(embed=fillembed(embed))
                    await context.message.add_reaction(self.client.check)

                elif operation == "-" or operation == "remove":
                    embed = discord.Embed(title="Cheeseballz Removed", color=0xff0000)
                    await self.client.logs.send(embed=fillembed(embed))
                    await context.message.add_reaction(self.client.check)

                elif operation == "set":
                    cbops.setcb(user.id, amount)
                    embed = discord.Embed(title="Cheeseballz Set", color=0xffff00)
                    await self.client.logs.send(embed=fillembed(embed))
                    await context.message.add_reaction(self.client.check)
                else:
                    await context.send(f"{context.author.mention} Command usage: `!cb <+/-/set> <@user> <amount> <reason>`")
        else:
            await main.noperms(context)

    @commands.command(name='balance', aliases=['bal', 'profile'])
    async def balance(self, context, *, user: discord.Member = None):
        async def getbal(user):
            bal = cbops.getbal(user.id)
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (user.id,))
            upgradelevel = str(c.fetchone()[0])
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (user.id,))
            currentgamble = str(c.fetchone()[0])
            c.execute("SELECT about FROM cheeseballztable WHERE userid=?", (user.id,))
            about = str(c.fetchone()[0])
            c.execute("SELECT daily FROM cheeseballztable WHERE userid=?", (user.id,))
            daily = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
            c.execute("SELECT weekly FROM cheeseballztable WHERE userid=?", (user.id,))
            weekly = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
            c.execute("SELECT monthly FROM cheeseballztable WHERE userid=?", (user.id,))
            monthly = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if daily + timedelta(hours=23) > now:
                dhours = (daily + timedelta(hours=23) - now).seconds // 3600
                dminutes = (daily + timedelta(hours=23) - now).seconds // 60 % 60
                dailytimeleft = f"{dhours} hours and {dminutes} minutes"
            else:
                dailytimeleft = "!daily available now"
            if weekly + timedelta(days=6, hours=23) > now:
                wdays = (weekly + timedelta(days=6, hours=23) - now).days
                whours = (weekly + timedelta(days=6, hours=23) - now).seconds // 3600
                wminutes = (weekly + timedelta(days=6, hours=23) - now).seconds // 60 % 60
                weeklytimeleft = f"{wdays} days, {whours} hours, and {wminutes} minutes"
            else:
                weeklytimeleft = "!weekly available now"
            if monthly + timedelta(days=29, hours=23) > now:
                mdays = (monthly + timedelta(days=29, hours=23) - now).days
                mhours = (monthly + timedelta(days=29, hours=23) - now).seconds // 3600
                mminutes = (monthly + timedelta(days=29, hours=23) - now).seconds // 60 % 60
                monthlytimeleft = f"{mdays} days, {mhours} hours, and {mminutes} minutes"
            else:
                monthlytimeleft = "!monthly available now"
            joindates = []
            uniquedate = user.joined_at
            for member in context.guild.members:
                joindates.append(member.joined_at)
            joindates.sort()
            embed = discord.Embed(title="", color=0x800080)
            embed.set_author(name=user, icon_url=user.avatar_url)
            embed.add_field(name="Date joined", value=user.joined_at.date(), inline=True)
            embed.add_field(name="Join position", value=int(joindates.index(uniquedate)) + 1, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="Balance", value=bal, inline=True)
            embed.add_field(name="Upgrade level", value=upgradelevel, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="Amount gambled today", value=currentgamble, inline=False)
            embed.add_field(name="Time until next !daily", value=dailytimeleft, inline=False)
            embed.add_field(name="Time until next !weekly", value=weeklytimeleft, inline=False)
            embed.add_field(name="Time until next !monthly", value=monthlytimeleft, inline=False)
            embed.add_field(name="About", value=about, inline=False)
            await context.send(embed=embed)

        if user is None:
            await getbal(context.author)
        else:
            await getbal(user)

    @commands.command(name='resetaccount', aliases=['resetacc'])
    async def resetaccount(self, context):
        defaulttime = "2020-01-01 00:00:00.000000"
        prevbal = cbops.getbal(context.author.id)
        c.execute("DELETE FROM cheeseballztable WHERE userid=?", (context.author.id,))
        c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly) VALUES (?, 0, 0, ?, ?, ?)", (context.author.id, defaulttime, defaulttime, defaulttime))
        conn.commit()
        await context.message.add_reaction(self.client.check)
        embed = discord.Embed(title="Account reset", color=0xff0000)
        embed.add_field(name="User", value=context.author.mention)
        embed.add_field(name="Previous balance", value=prevbal)
        await self.client.logs.send(embed=embed)

    @commands.command(name='shop')
    async def shop(self, context):
        balance = cbops.getbal(context.author.id)
        c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
        upgradelevel = int(c.fetchone()[0])
        embed = discord.Embed(title="Shop", description="Purchase items with !buy <number>, sell items with !sell <number>", color=0xb200b2)
        embed.set_footer(text=f"Your balance: {balance}")
        embed.add_field(name="1. Nscheeseballz Chat Permissions", value="Buy: 20,000 cb | Sell: 19,000 cb", inline=False)
        embed.add_field(name="2. Omega Special Role", value="Buy: 5,000 cb | Sell: 4,500 cb", inline=False)
        embed.add_field(name="3. ;) role", value="Buy: 1,000 cb | Sell: 900 cb", inline=False)
        embed.add_field(name="4. DJ role", value="Buy: 5,000 cb | Sell: 4,500 cb", inline=False)
        embed.add_field(name="5. Exclusive giveaway channel role", value="Buy: 9,000 cb | Sell: 8,100 cb", inline=False)
        embed.add_field(name="6. uwu role", value="Buy: 2,000 cb | Sell: 1,800 cb", inline=False)
        embed.add_field(name="7. owo role", value="Buy: 2,000 cb | Sell: 1,800 cb", inline=False)
        embed.add_field(name="8. Custom role", value="Buy: 30,000 cb", inline=False)
        embed.add_field(name=f"9. Increase upgrade level - Level {upgradelevel} to {upgradelevel + 1}", value="Buy: 10,000 cb", inline=False)
        await context.send(embed=embed)

    @commands.command(name='buy', aliases=['purchase'])
    async def buy(self, context, selection: int = 0):
        nscheeseballz = self.client.crdguild.get_role(674479777444265985)
        omega = self.client.crdguild.get_role(674478322687672351)
        wink = self.client.crdguild.get_role(674481196239028235)
        dj = self.client.crdguild.get_role(688601672766849025)
        richman = self.client.crdguild.get_role(704053604172038184)
        uwu = self.client.crdguild.get_role(714783199170920508)
        owo = self.client.crdguild.get_role(725292693487485018)
        # --
        bal = cbops.getbal(context.author.id)

        async def role(role, amount):
            if bal < amount:
                await cbops.insufficientcb(context)
            else:
                cbops.removecb(context.author.id, amount)
                await context.send(f"{context.author.mention} {self.client.check} Purchase successful.")
                await context.author.add_roles(role, reason="Purchased from cheeseballz shop")
                embed = discord.Embed(title="Role Purchased", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=False)
                embed.add_field(name="Role", value=role.mention, inline=False)
                await self.client.logs.send(embed=embed)

        if selection == 1:
            await role(nscheeseballz, 20000)
        elif selection == 2:
            await role(omega, 5000)
        elif selection == 3:
            await role(wink, 1000)
        elif selection == 4:
            await role(dj, 5000)
        elif selection == 5:
            await role(richman, 9000)
        elif selection == 6:
            await role(uwu, 2000)
        elif selection == 7:
            await role(owo, 2000)
        elif selection == 8:
            if bal < 30000:
                await cbops.insufficientcb(context)
            else:
                checkmsg = await context.send(f"""{context.author.mention} Purchasing a custom role for 30,000 cb.
- You have 60 seconds to respond to each question.
- You may cancel by ignoring the question for 60 seconds.
- I suggest making the role you want in your own server first, to ensure names and hex color codes work.
Click the checkmark to continue once you're ready.""")
                await checkmsg.add_reaction(self.client.check)

                def readycheck(reaction, member):
                    return reaction.emoji == self.client.check and member == context.author

                def messageresponsecheck(m):
                    return m.author == context.author and m.channel == context.channel

                def reactionresponsecheck(reaction, member):
                    return (reaction.emoji == self.client.check or reaction.emoji == self.client.x) and member == context.author and reaction.message.channel == context.channel

                try:
                    await self.client.wait_for('reaction_add', check=readycheck, timeout=300)
                    await context.send("Type the new role name.")
                    rolenamemsg = await self.client.wait_for('message', check=messageresponsecheck, timeout=60)
                    await context.send(
                        "Type the __HEX__ code for your role color. You can find these by Googling 'color picker'.")
                    hexmsg = await self.client.wait_for('message', check=messageresponsecheck, timeout=60)
                    hoistquestion = await context.send("Should the role be shown in the member list?")
                    await hoistquestion.add_reaction(self.client.check)
                    await hoistquestion.add_reaction(self.client.x)
                    reaction, user = await self.client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                    if reaction.emoji == self.client.check:
                        hoist = True
                    elif reaction.emoji == self.client.x:
                        hoist = False
                    mentionablequestion = await context.send("Should the role be mentionable by everyone?")
                    await mentionablequestion.add_reaction(self.client.check)
                    await mentionablequestion.add_reaction(self.client.x)
                    reaction, user = await self.client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                    if reaction.emoji == self.client.check:
                        mentionable = True
                    elif reaction.emoji == self.client.x:
                        mentionable = False
                    await context.send(
                        f"{context.author.mention} Creating role `{rolenamemsg.content}` with hex color `{hexmsg.content}`.")
                    try:
                        if '#' in hexmsg.content:
                            fixedhex = re.sub("[#]", "", hexmsg.content)
                        else:
                            fixedhex = hexmsg.content
                        hexcode = discord.Color(int(fixedhex, 16))
                        newrole = await context.guild.create_role(name=rolenamemsg.content, color=hexcode,
                                                                  hoist=hoist, mentionable=mentionable,
                                                                  reason=f"Created by {context.author.id}, custom role from shop.")
                        await newrole.edit(position=12)
                        await context.author.add_roles(newrole)
                        await context.send(f"{context.author.mention} Role created and assigned to you.")
                        embed = discord.Embed(name="Custom role created", color=0xffff00)
                        embed.add_field(name="User", value=context.author.mention, inline=False)
                        embed.add_field(name="Role name", value=rolenamemsg.content, inline=False)
                        embed.add_field(name="Role color", value=hexmsg.content, inline=False)
                        await self.client.logs.send(embed=embed)
                        cbops.removecb(context.author.id, 30000)
                        conn.commit()
                    except:
                        await context.send(f"{context.author.mention} One or more fields had an invalid input. Try again.")
                except asyncio.TimeoutError:
                    await context.send(f"{context.author.mention} Timed out, cancelling.")
        elif selection == 9:
            if bal < 10000:
                await context.send(f"{context.author.mention} {self.client.x} Not enough cheeseballz.")
            else:
                cbops.removecb(context.author.id, 10000)
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                upgrade = int(c.fetchone()[0]) + 1
                c.execute("UPDATE cheeseballztable SET upgradelevel=? WHERE userid=?", (upgrade, context.author.id))
                conn.commit()
                await context.send(f"{context.author.mention} {self.client.check} Purchase successful.")
                embed = discord.Embed(title="Upgrade Level Increased", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=False)
                embed.add_field(name="New Upgrade Level", value=upgrade, inline=False)
                await self.client.logs.send(embed=embed)
        else:
            await context.send(f"{context.author.mention} Select a valid item in the shop. Use `!shop` to list items.")

    @commands.command(name='sell', aliases=['refund'])
    async def sell(self, context, selection: int = 0):
        nscheeseballz = self.client.crdguild.get_role(674479777444265985)
        omega = self.client.crdguild.get_role(674478322687672351)
        wink = self.client.crdguild.get_role(674481196239028235)
        dj = self.client.crdguild.get_role(688601672766849025)
        richman = self.client.crdguild.get_role(704053604172038184)
        uwu = self.client.crdguild.get_role(714783199170920508)
        owo = self.client.crdguild.get_role(725292693487485018)

        async def role(role, amount):
            if role in context.author.roles:
                cbops.addcb(context.author.id, amount)
                await context.author.remove_roles(role, reason="Sold to cheeseballz shop")
                await context.send(f"{context.author.mention} {self.client.check} Refund successful. Received {amount} cheeseballz.")
                embed = discord.Embed(title="Role sold", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=False)
                embed.add_field(name="Role", value=role.mention, inline=False)
                await self.client.logs.send(embed=embed)
            else:
                await context.send(f"{context.author.mention} {self.client.x} You don't have the specified role to sell.")

        if selection == 1:
            await role(nscheeseballz, 19000)
        elif selection == 2:
            await role(omega, 4500)
        elif selection == 3:
            await role(wink, 900)
        elif selection == 4:
            await role(dj, 4500)
        elif selection == 5:
            await role(richman, 8100)
        elif selection == 6:
            await role(uwu, 1800)
        elif selection == 7:
            await role(owo, 1800)
        else:
            await context.send(
                f"{context.author.mention} Select a valid role in the shop. Use `!shop` to list items.")

    @commands.command(name='send', aliases=['pay'])
    async def send(self, context, user: discord.Member = None, amount: int = None):
        if user is None or amount is None:
            await context.send(f"{context.author.mention} Command usage: `!send <@user> <amount>`")
        else:
            if amount < 1:
                await context.send(f"{context.author.mention} {self.client.x} You must send at least one cb.")
            else:
                bal = cbops.getbal(context.author.id)
                if bal < amount:
                    await cbops.insufficientcb(context)
                else:
                    cbops.removecb(context.author.id, amount)
                    cbops.addcb(user.id, amount)
                    await context.message.add_reaction(self.client.check)
                    embed = discord.Embed(title="Cheeseballz Sent", color=0xffff00)
                    embed.add_field(name="From user", value=context.author.mention, inline=False)
                    embed.add_field(name="To user", value=user.mention, inline=True)
                    embed.add_field(name="Amount", value=amount, inline=True)
                    await self.client.logs.send(embed=embed)

    @commands.command(name='daily', aliases=['d'])
    async def daily(self, context):
        c.execute("SELECT daily FROM cheeseballztable WHERE userid=?", (context.author.id,))
        daily = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.now()
        if daily + timedelta(hours=23) > now:
            dhours = (daily + timedelta(hours=23) - now).seconds // 3600
            dminutes = (daily + timedelta(hours=23) - now).seconds // 60 % 60
            await context.send(f"{context.author.mention} {self.client.x} Your daily cheeseballz resets in **{dhours} hours and {dminutes} minutes.**")
        else:
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
            upgradelevel = int(c.fetchone()[0])
            lower = 100 + (upgradelevel * 100)
            upper = 200 + (upgradelevel * 100)
            bal = cbops.getbal(context.author.id)
            amount = random.randint(lower, upper)
            cbops.addcb(context.author.id, amount)
            c.execute("UPDATE cheeseballztable SET daily=? WHERE userid=?", (now, context.author.id))
            conn.commit()
            await context.send(f"{context.author.mention} {self.client.check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")

    @commands.command(name='weekly', aliases=['w'])
    async def weekly(self, context):
        c.execute("SELECT weekly FROM cheeseballztable WHERE userid=?", (context.author.id,))
        weekly = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.now()
        if weekly + timedelta(days=6, hours=23) > now:
            wdays = (weekly + timedelta(days=6, hours=23) - now).days
            whours = (weekly + timedelta(days=6, hours=23) - now).seconds // 3600
            wminutes = (weekly + timedelta(days=6, hours=23) - now).seconds // 60 % 60
            await context.send(f"{context.author.mention} {self.client.x} Your weekly cheeseballz resets in **{wdays} days, {whours} hours, and {wminutes} minutes.**")
        else:
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
            upgradelevel = int(c.fetchone()[0])
            lower = 600 + (upgradelevel * 200)
            upper = 800 + (upgradelevel * 200)
            bal = cbops.getbal(context.author.id)
            amount = random.randint(lower, upper)
            cbops.addcb(context.author.id, amount)
            c.execute("UPDATE cheeseballztable SET weekly=? WHERE userid=?", (now, context.author.id))
            conn.commit()
            await context.send(f"{context.author.mention} {self.client.check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")

    @commands.command(name='monthly', aliases=['m'])
    async def monthly(self, context):
        c.execute("SELECT monthly FROM cheeseballztable WHERE userid=?", (context.author.id,))
        monthly = datetime.strptime(str(c.fetchone()[0]), '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.now()
        if monthly + timedelta(days=29, hours=23) > now:
            mdays = (monthly + timedelta(days=29, hours=23) - now).days
            mhours = (monthly + timedelta(days=29, hours=23) - now).seconds // 3600
            mminutes = (monthly + timedelta(days=29, hours=23) - now).seconds // 60 % 60
            await context.send(f"{context.author.mention} {self.client.x} Your monthly cheeseballz resets in **{mdays} days, {mhours} hours, and {mminutes} minutes.**")
        else:
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
            upgradelevel = int(c.fetchone()[0])
            lower = 1500 + (upgradelevel * 500)
            upper = 2000 + (upgradelevel * 500)
            bal = cbops.getbal(context.author.id)
            amount = random.randint(lower, upper)
            cbops.addcb(context.author.id, amount)
            c.execute("UPDATE cheeseballztable SET monthly=? WHERE userid=?", (now, context.author.id))
            conn.commit()
            await context.send(f"{context.author.mention} {self.client.check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")

    @commands.command(name='total')
    async def total(self, context):
        c.execute("SELECT SUM(cheeseballz) FROM cheeseballztable")
        total = int(c.fetchone()[0])
        cbexcluded = context.guild.get_role(726974805831843900)
        for member in cbexcluded.members:
            total = total - cbops.getbal(member.id)
        await context.send(f"The guild currently has {total} cheeseballz stored.")

    @commands.command(name='leaderboard', aliases=['top', 'lb'])
    async def leaderboard(self, context, page: int = 1):
        if page <= 5:
            msg = await context.send("Sorting...")
            cbexcluded = context.guild.get_role(726974805831843900)
            userdict = {}
            userlist = []
            i = 0
            while True:
                c.execute("SELECT userid FROM cheeseballztable ORDER BY cheeseballz DESC LIMIT 1 OFFSET ?", (i,))
                userid = int(c.fetchone()[0])
                try:
                    member = context.guild.get_member(userid)
                    if cbexcluded in member.roles:
                        pass
                    else:
                        userdict[userid] = cbops.getbal(userid)
                        userlist.append(userid)
                except AttributeError:
                    pass
                if len(userlist) == 30:
                    break
                i = i + 1

            async def generate_leaderboard(page):
                embed = discord.Embed(title="Cheeseballz Leaderboard", description=f"Page {page}", color=0xffa500)
                upper = page * 10
                lower = upper - 10
                for i in range(lower, upper):
                    embed.add_field(name="-------",
                                    value=f"{i + 1}. <@{userlist[i]}> - {userdict[userlist[i]]} cheeseballz",
                                    inline=False)
                await msg.edit(content=None, embed=embed)

            while True:
                await generate_leaderboard(page)
                if page == 1:
                    await msg.add_reaction(u"\U000027a1")  # arrow pointing right
                elif page == 3:
                    await msg.add_reaction(u"\U00002b05")  # arrow pointing left
                else:
                    await msg.add_reaction(u"\U00002b05")  # arrow pointing left
                    await msg.add_reaction(u"\U000027a1")  # arrow pointing right

                def check(reaction, user):
                    return user == context.message.author and (
                            str(reaction.emoji) == '➡' or str(reaction.emoji) == '⬅')

                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=10, check=check)
                    if str(reaction.emoji) == '⬅':
                        page = page - 1
                    elif str(reaction.emoji) == '➡':
                        page = page + 1
                    await msg.clear_reactions()
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break
        else:
            await context.send(f"{context.author.mention} Select a valid page. Pages range from 1-3.")

    @commands.command(name='setabout')
    async def setabout(self, context, *, about: str = None):
        if about is None:
            await context.send(f"{context.author.mention} Command usage: `!setabout <about>`")
        elif len(about) > 500:
            await context.send(f"{context.author.mention} {self.client.x} Too many characters. The limit is 500; you currently have {len(about)}.")
        else:
            c.execute("UPDATE cheeseballztable SET about=? WHERE userid=?", (about, context.author.id))
            conn.commit()
            embed = discord.Embed(title="About Changed", color=0xc6c6c6)
            embed.add_field(name="User", value=context.author.mention, inline=True)
            embed.add_field(name="New content", value=about, inline=True)
            await self.client.logs.send(embed=embed)
            await context.message.add_reaction(self.client.check)

    @commands.command(name='request', aliases=['req'])
    async def request(self, context, operation: str = None, user: discord.Member = None, amount: int = None, *, reason: str = None):
        staff = context.guild.get_role(564649798196658186)
        if operation is None or user is None or amount is None or reason is None or amount <= 0:
            await context.send(f"{context.author.mention} Command usage: `!request <+/-> <@user> <amount> <reason>`")
        elif staff in context.author.roles:
            def createEmbed(color):
                embed = discord.Embed(title="Cheeseballz Request", color=color)
                embed.add_field(name="Staff member", value=context.author.mention, inline=False)
                embed.add_field(name="User", value=user.mention, inline=False)
                embed.add_field(name="Operation", value=operation, inline=False)
                embed.add_field(name="Amount", value=amount, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                return embed

            embed = createEmbed(0x6c6c6c)
            reqmsg = await self.client.requests.send(embed=embed)
            logmsg = await self.client.logs.send(embed=embed)
            await reqmsg.add_reaction(self.client.check)
            await reqmsg.add_reaction(self.client.x)
            await context.message.add_reaction(self.client.check)

            def reactioncheck(reaction, member):
                return (reaction.emoji == self.client.check or reaction.emoji == self.client.x) and reaction.message.id == reqmsg.id and self.client.cbperms in member.roles

            reaction, member = await self.client.wait_for('reaction_add', check=reactioncheck)
            if reaction.emoji == self.client.check:
                embed = createEmbed(0x00ff00)
                embed.add_field(name="Accepted by", value=member.mention, inline=False)
                await reqmsg.edit(embed=embed)
                await logmsg.edit(embed=embed)
                await reqmsg.clear_reactions()
                if operation == '+':
                    cbops.addcb(user.id, amount)
                elif operation == '-':
                    cbops.removecb(user.id, amount)
            elif reaction.emoji == self.client.x:
                embed = createEmbed(0xff0000)
                embed.add_field(name="Denied by", value=member.mention, inline=False)
                await reqmsg.edit(embed=embed)
                await logmsg.edit(embed=embed)
                await reqmsg.clear_reactions()
        else:
            await main.noperms(context)

    @commands.command(name="slots")
    @commands.cooldown(rate=1, per=4, type=BucketType.member)
    async def slots(self, context, amount: int = None):
        bal = cbops.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!slots <amount>`")
        elif amount < 50:
            await context.send(f"{context.author.mention} You must bet a minimum of 50 cheeseballz. You currently have {bal} cheeseballz.")
        else:
            if bal < amount:
                await cbops.insufficientcb(context)
            else:
                c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
                currentgamble = int(c.fetchone()[0])
                c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
                conn.commit()
                cbops.removecb(context.author.id, amount)
                roll = ['empty']
                for i in range(18):
                    roll.append(random.choice([':strawberry:', ':pear:', ':tangerine:', ':grapes:', ':watermelon:']))
                message = await context.send(f"""{context.author.mention} Slots:
:heavy_minus_sign:{roll[1]} | {roll[2]} | {roll[3]}:heavy_minus_sign:
:arrow_forward:{roll[4]} | {roll[5]} | {roll[6]}:arrow_backward:
:heavy_minus_sign:{roll[7]} | {roll[8]} | {roll[9]}:heavy_minus_sign:""")
                await asyncio.sleep(0.5)
                await message.edit(content=f"""{context.author.mention} Slots:
:heavy_minus_sign:{roll[4]} | {roll[5]} | {roll[6]}:heavy_minus_sign:
:arrow_forward:{roll[7]} | {roll[8]} | {roll[9]}:arrow_backward:
:heavy_minus_sign:{roll[10]} | {roll[11]} | {roll[12]}:heavy_minus_sign:""")
                await asyncio.sleep(0.5)
                await message.edit(content=f"""{context.author.mention} Slots:
:heavy_minus_sign:{roll[7]} | {roll[8]} | {roll[9]}:heavy_minus_sign:
:arrow_forward:{roll[10]} | {roll[11]} | {roll[12]}:arrow_backward:
:heavy_minus_sign:{roll[13]} | {roll[14]} | {roll[15]}:heavy_minus_sign:""")
                await asyncio.sleep(0.5)
                await message.edit(content=f"""{context.author.mention} Slots:
:heavy_minus_sign:{roll[10]} | {roll[11]} | {roll[12]}:heavy_minus_sign:
:arrow_forward:{roll[13]} | {roll[14]} | {roll[15]}:arrow_backward:
:heavy_minus_sign:{roll[16]} | {roll[17]} | {roll[18]}:heavy_minus_sign:""")
                if roll[13] == roll[14] and roll[14] == roll[15]:
                    await context.send(f"{context.author.mention} Congrats! Received {amount * 12} cheeseballz back.")
                    winnings = amount * 12
                    cbops.addcb(context.author.id, winnings)
                else:
                    await context.send(f"{context.author.mention} Sorry, try again.")

    @commands.command(name='russianroulette', aliases=['rr', 'russian-roulette'])
    async def russianroulette(self, context, operation: str = None, gameid: int = None, amount: int = None):
        if operation is None or gameid is None:
            await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")
        else:
            bal = cbops.getbal(context.author.id)

            async def startgame(gameid):
                c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                if str(c.fetchone()[0]) == 'None':
                    await context.send(f"{context.author.mention} Two or more players are required to start.")
                else:
                    c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                    player1 = str(c.fetchone()[0])
                    if str(context.author.id) == player1:
                        c.execute("UPDATE russianroulette SET started=1 WHERE gameid=?", (gameid,))
                        await context.send(f"{context.author.mention} Starting game {gameid}.")
                        players = []
                        toRemove = []
                        ended = False
                        for i in range(1, 7):
                            playernum = ('player' + str(i))
                            c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?", (gameid,))
                            player = str(c.fetchone()[0])
                            if player != 'None':
                                players.append(player)
                        originalPlayers = len(players)

                        # functions
                        def refreshchamber():
                            functionchamber = []
                            for i in range(len(players)):
                                choice = random.randint(0, 1)
                                functionchamber.append(choice)
                            return functionchamber

                        chamber = refreshchamber()

                        async def fire(fireindex):
                            await asyncio.sleep(2)
                            if chamber[fireindex] == 0:
                                await context.send(f"<@{players[fireindex]}> pulls the trigger and... survives!")
                            else:
                                await context.send(f"<@{players[fireindex]}> pulls the trigger and... gets shot!")
                                return fireindex

                        # actual
                        while ended is False:
                            chamber = refreshchamber()
                            for i in range(len(players)):
                                pending = await fire(i)
                                if pending is not None:
                                    toRemove.append(pending)
                            if toRemove != []:
                                toRemove.reverse()
                                for i in toRemove:
                                    players.pop(i)
                                    toRemove = []
                            if len(players) <= 1:
                                if len(players) == 0:
                                    await context.send(f"No one won game {gameid}.")
                                    ended = True
                                    c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                    conn.commit()
                                else:
                                    await context.send(f"<@{players[0]}> has won the game!")
                                    c.execute("SELECT bet FROM russianroulette WHERE gameid=?", (gameid,))
                                    toAdd = int(c.fetchone()[0]) * originalPlayers
                                    cbops.addcb(int(players[0]), toAdd)
                                    await context.send(f"{toAdd} cheeseballz has been deposited to <@{players[0]}>'s account.")
                                    c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                    conn.commit()
                                    ended = True
                    else:
                        if player1 == '':
                            await context.send(f"{context.author.mention} The specified game does not exist.")
                        else:
                            await context.send(f"{context.author.mention} Only the host can start the game.")

            if operation == 'new':
                if amount is None:
                    await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")
                else:
                    c.execute("SELECT COUNT(1) FROM russianroulette WHERE gameid=?", (gameid,))
                    if str(c.fetchone()[0]) != '0':
                        await context.send(f"{context.author.mention} A game with this ID already exists. Pick a different ID.")
                    else:
                        if amount <= 0:
                            await context.send(f"{context.author.mention} You must bet more than 0 cheeseballz. You currently have {bal} cheeseballz.")
                        else:
                            if amount > bal:
                                await cbops.insufficientcb(context)
                            else:
                                c.execute("INSERT INTO russianroulette(gameid, bet, player1, started) VALUES (?, ?, ?, 0)", (gameid, amount, context.author.id))
                                cbops.removecb(context.author.id, amount)
                                embed = discord.Embed(title="Started Russian Roulette", color=0x0000ff)
                                embed.add_field(name="User", value=context.author.mention, inline=True)
                                embed.add_field(name="Amount", value=amount, inline=True)
                                await self.client.logs.send(embed=embed)
                                conn.commit()
                                embed = discord.Embed(title="Russian Roulette", color=0xffa500)
                                embed.add_field(name="Game ID", value=gameid, inline=False)
                                embed.add_field(name="Bet", value=amount, inline=False)
                                embed.add_field(name="Player 1", value=context.author.mention)
                                await context.send(embed=embed)
                                await asyncio.sleep(30)
                                c.execute("SELECT started FROM russianroulette WHERE gameid=?", (gameid,))
                                if str(c.fetchone()[0]) == '0':
                                    await context.send(f"{context.author.mention} 30 second timeout passed. Automatically starting game {gameid}.")
                                    c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                                    if str(c.fetchone()[0]) == 'None':
                                        await context.send(f"{context.author.mention} Not enough players to start game automatically. Deleting game, refunding {amount} cheeseballz.")
                                        cbops.addcb(context.author.id, amount)
                                        c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                        conn.commit()
                                    else:
                                        await startgame(gameid)
            elif operation == 'join':
                if gameid == 0:
                    await context.send(f"{context.author.mention} Specify a valid game id.")
                else:
                    c.execute("SELECT started FROM russianroulette WHERE gameid=?", (gameid,))
                    if str(c.fetchone()[0]) == '1':
                        await context.send(f"{context.author.mention} This game has already started.")
                    else:
                        c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                        if str(c.fetchone()[0]) == context.author.id:
                            await context.send(f"{context.author.mention} You are already in this game.")
                        else:
                            c.execute("SELECT player6 FROM russianroulette WHERE gameid=?", (gameid,))
                            if str(c.fetchone()[0]) != 'None':
                                c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                                if str(c.fetchone()[0]) != 'None':
                                    await context.send(f"{context.author.mention} Specify a valid game id.")
                                else:
                                    await context.send(f"{context.author.mention} This game is already full.")
                            else:
                                c.execute("SELECT bet FROM russianroulette WHERE gameid=?", (gameid,))
                                amount = int(c.fetchone()[0])
                                if amount > bal:
                                    await cbops.insufficientcb(context)
                                else:
                                    async def join(playernum):
                                        c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?",
                                                  (gameid,))
                                        if str(c.fetchone()[0]) == 'None':
                                            c.execute(f"UPDATE russianroulette SET {playernum}=? WHERE gameid=?",
                                                      (context.author.id, gameid))
                                            newbalance = bal - amount
                                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?",
                                                      (newbalance, context.author.id,))
                                            embed = discord.Embed(title="Joined Russian Roulette", color=0x0000ff)
                                            embed.add_field(name="User", value=context.author.mention, inline=True)
                                            embed.add_field(name="Amount", value=amount, inline=True)
                                            await self.client.logs.send(embed=embed)
                                            conn.commit()
                                            await context.send(f"{context.author.mention} Joined game {gameid}, betting {amount} cheeseballz.")
                                            return True
                                        else:
                                            return False

                                    for i in range(2, 7):
                                        playernum = ('player' + str(i))
                                        if await join(playernum) is True:
                                            break
                                    embed = discord.Embed(title="Russian Roulette", color=0xffa500)
                                    embed.add_field(name="Game ID", value=gameid, inline=False)
                                    embed.add_field(name="Bet", value=amount, inline=False)
                                    # first player---
                                    c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                                    player1 = str(c.fetchone()[0])
                                    embed.add_field(name="Player 1", value=f"<@{player1}>", inline=False)
                                    # second player---
                                    c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                                    player2 = str(c.fetchone()[0])
                                    embed.add_field(name="Player 2", value=f"<@{player2}>", inline=False)
                                    # check for third-sixth
                                    for i in range(3, 7):
                                        c.execute(f"SELECT {('player' + str(i))} FROM russianroulette WHERE gameid=?", (gameid,))
                                        playernum = str(c.fetchone()[0])
                                        if playernum != 'None':
                                            embed.add_field(name=f"Player {i}", value=f"<@{playernum}>", inline=False)
                                    await context.send(embed=embed)
            elif operation == 'start':
                await startgame(gameid)
            else:
                await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")

    @commands.command(name='double', aliases=['dub', 'doub'])
    @commands.cooldown(rate=1, per=2, type=BucketType.member)
    async def double(self, context, amount: int = None):
        bal = cbops.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!double <amount>`")
        elif amount > bal:
            await cbops.insufficientcb(context)
        elif amount < 1:
            await context.send(f"{context.author.mention} You must bet at least one cheeseballz.")
        else:
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
            currentgamble = int(c.fetchone()[0])
            c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
            conn.commit()
            cbops.removecb(context.author.id, amount)
            if random.choice([True, False]) is True:
                await context.send(f"{context.author.mention} Congrats! Received {amount*2} cheeseballz back.")
                cbops.addcb(context.author.id, amount*2)
            else:
                await context.send(f"{context.author.mention} Sorry, try again.")

    @commands.command(name='mcheeseballz', aliases=['mcb'])
    async def mcheeseballz(self, context, operation: str = None, amount: int = None, *, users: str = None):
        if operation is None or amount is None or users is None:
            await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
        else:
            if self.client.cbperms in context.author.roles or context.author.guild_permissions.administrator:
                users = re.sub("[<@!>]", "", users)
                userlist = users.split()
                for userid in userlist:
                    if operation == '+':
                        cbops.addcb(amount, userid)
                    elif operation == '-':
                        cbops.removecb(amount, userid)
                    else:
                        await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
                        break
                embed = discord.Embed(title="Multiple cheeseballz transactions", color=0xffff00)
                embed.add_field(name="Staff", value=context.author.mention, inline=False)
                embed.add_field(name="Operation", value=operation, inline=False)
                embed.add_field(name="Amount", value=amount, inline=False)
                embed.add_field(name="User IDs", value=userlist, inline=False)
                await self.client.logs.send(embed=embed)
                conn.commit()
                await context.message.add_reaction(self.client.check)
            else:
                await main.noperms(context)

    @commands.command(name='mrequest', aliases=['mreq'])
    async def mrequest(self, context, operation: str = None, amount: int = None, *, users: str = None):
        if operation is None or amount is None or users is None:
            await context.send(f"{context.author.mention} Command usage: `!mreq <+/-> <amount> <@users>`")
        else:
            staff = context.guild.get_role(564649798196658186)
            if staff in context.author.roles:
                await context.send(f"{context.author.mention} Reason?")

                def messagecheck(m):
                    return m.author == context.author and m.channel == context.channel

                try:
                    reason = await self.client.wait_for('message', check=messagecheck, timeout=30)
                except asyncio.TimeoutError:
                    reason = None
                if reason is None:
                    await context.send(f"{context.author.mention} Reason field was empty or timed out. Try again.")
                else:
                    users = re.sub("[<@!>]", "", users)
                    userlist = users.split()
                    userid = 0
                    reqmsgs = []

                    def createEmbed(color):
                        embed = discord.Embed(title="Multiple Cheeseballz Requests", color=color)
                        embed.add_field(name="Staff member", value=context.author.mention, inline=False)
                        embed.add_field(name="User", value=f"<@{userid}>", inline=False)
                        embed.add_field(name="Operation", value=operation, inline=False)
                        embed.add_field(name="Amount", value=amount, inline=False)
                        embed.add_field(name="Reason", value=reason.content, inline=False)
                        return embed

                    for userid in userlist:
                        embed = createEmbed(0x6c6c6c)
                        reqmsg = await self.client.requests.send(embed=embed)
                        logmsg = await self.client.logs.send(embed=embed)
                        await reqmsg.add_reaction(self.client.check)
                        await reqmsg.add_reaction(self.client.x)
                        reqmsgs.append(reqmsg)
                    await context.message.add_reaction(self.client.check)
                    for reqmsg in reqmsgs:
                        def reactioncheck(reaction, member):
                            return (reaction.emoji == self.client.check or reaction.emoji == self.client.x) and reaction.message.id == reqmsg.id and self.client.cbperms in member.roles

                        reaction, member = await self.client.wait_for('reaction_add', check=reactioncheck)
                        if reaction.emoji == self.client.check:
                            embed = createEmbed(0x00ff00)
                            embed.add_field(name="Accepted by", value=member.mention, inline=False)
                            await reqmsg.edit(embed=embed)
                            await logmsg.edit(embed=embed)
                            await reqmsg.clear_reactions()
                            if operation == '+':
                                cbops.addcb(userid, amount)
                            elif operation == '-':
                                cbops.removecb(userid, amount)
                        elif reaction.emoji == self.client.x:
                            embed = createEmbed(0xff0000)
                            embed.add_field(name="Denied by", value=member.mention, inline=False)
                            await reqmsg.edit(embed=embed)
                            await logmsg.edit(embed=embed)
                            await reqmsg.clear_reactions()
            else:
                await main.noperms(context)

    @commands.command(name='blackjack', aliases=['bj'])
    @commands.cooldown(rate=2, per=20, type=BucketType.member)
    async def blackjack(self, context, amount: int = None):
        bal = cbops.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!blackjack <amount>`")
        elif amount < 50:
            await context.send(f"{context.author.mention} You must bet at least 50 cheeseballz.")
        elif bal < amount:
            await cbops.insufficientcb(context)
        else:
            cbops.removecb(context.author.id, amount)
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
            currentgamble = int(c.fetchone()[0])
            c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
            conn.commit()
            suits = [':hearts:', ':spades:', ':clubs:', ':diamonds:']
            cardvalues = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 'Ace']  # multiple 10s to make up for the j, q, and k
            dealer1value = random.choice(cardvalues)
            dealer1suit = random.choice(suits)
            dealer2value = random.choice(cardvalues)
            dealer2suit = random.choice(suits)
            player1value = random.choice(cardvalues)
            player1suit = random.choice(suits)
            player2value = random.choice(cardvalues)
            player2suit = random.choice(suits)
            await context.send(f"""{context.author.mention} Dealer's face up card is a {dealer1value} of {dealer1suit}.

Your cards are:
- {player1value} of {player1suit}
- {player2value} of {player2suit}""")

            dealercalc = False
            playercalc = False
            if dealer1value == 'Ace' or dealer2value == 'Ace':
                dealercalc = True
                if dealer1value == 10 or dealer2value == 10:
                    dealertotal = 21
                elif dealer1value == dealer2value:
                    dealertotal = 12
                else:
                    if dealer1value == 'Ace':
                        dealertotal = 11 + dealer2value
                    elif dealer2value == 'Ace':
                        dealertotal = 11 + dealer1value
            if dealercalc is False:
                dealertotal = dealer1value + dealer2value
            if player1value == 'Ace' or player2value == 'Ace':
                playercalc = True
                if player1value == 10 or player2value == 10:
                    await context.send(f"{context.author.mention} Blackjack. Received {amount*3} cheeseballz back.")
                    cbops.addcb(context.author.id, amount*3)
                elif player1value == player2value:
                    playertotal = 12
                else:
                    if player1value == 'Ace':
                        playertotal = 11 + player2value
                    elif player2value == 'Ace':
                        playertotal = 11 + player1value
            if playercalc is False:
                playertotal = player1value + player2value

            def msgcheck(m):
                return m.author == context.author and m.channel == context.channel

            while True:
                await context.send("Type `hit` or `h` to hit, `stand` or `s` to stand.")
                response = await self.client.wait_for('message', check=msgcheck)
                if response.content.lower() == 'h' or response.content.lower() == 'hit':
                    playernewcardvalue = random.choice(cardvalues)
                    playernewcardsuit = random.choice(suits)
                    if playernewcardvalue == 'Ace':
                        if playertotal + 11 > 21:
                            playertotal = playertotal + 1
                            await context.send(
                                f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}. It has been set to 1.")
                        else:
                            playertotal = playertotal + 11
                            await context.send(
                                f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}. It has been set to 11.")
                    else:
                        playertotal = playertotal + playernewcardvalue
                        await context.send(
                            f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}.")
                    if playertotal == 21:
                        await context.send(f"{context.author.mention} You have a total of 21, standing.")
                        break
                    elif playertotal > 21:
                        await context.send(f"{context.author.mention} Bust. Dealer wins.")
                        break
                elif response.content.lower() == 's' or response.content.lower() == 'stand':
                    await context.send(f"{context.author.mention} Standing with a value of {playertotal}.")
                    break
                else:
                    await context.send(f"{context.author.mention} Invalid response.")
            if playertotal <= 21:
                dealermsg = f"""{context.author.mention} Dealer cards:
- {dealer1value} of {dealer1suit}
- {dealer2value} of {dealer2suit}"""
                dealersend = await context.send(dealermsg)
                while True:
                    if dealertotal >= 17:
                        break
                    dealernewcardsuit = random.choice(suits)
                    dealernewcardvalue = random.choice(cardvalues)
                    if dealernewcardvalue == 'Ace':
                        if dealertotal + 11 > 21:
                            dealertotal = dealertotal + 1
                        else:
                            dealertotal = dealertotal + 11
                    else:
                        dealertotal = dealertotal + dealernewcardvalue
                    dealermsg = dealermsg + f"\n- {dealernewcardvalue} of {dealernewcardsuit}"
                    await dealersend.edit(content=dealermsg)
                    await asyncio.sleep(0.25)
                if dealertotal > 21:
                    await context.send(f"{context.author.mention} Dealer bust. Received {amount*2}.")
                    cbops.addcb(context.author.id, amount*2)
                elif dealertotal == playertotal:
                    await context.send(f"{context.author.mention} Push. Received {amount}.")
                    cbops.addcb(context.author.id, amount)
                elif dealertotal > playertotal:
                    await context.send(f"{context.author.mention} Dealer wins.")
                else:
                    await context.send(f"{context.author.mention} You won. Received {amount * 2}.")
                    cbops.addcb(context.author.id, amount*2)


def setup(client):
    client.add_cog(Cheeseballz(client))
