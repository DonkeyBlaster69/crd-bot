import discord
import random
import re
import asyncio
from datetime import datetime, timedelta
import sqlite3
from discord.ext import commands
from discord.ext.commands import BucketType
import funcs

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()


class Cheeseballz(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='cbsql')
    @commands.is_owner()
    async def cbsql(self, context, *, command: str = None):
        if command is None:
            await context.send(f"{context.author.mention} Command usage: `!cbsql <command>`")
        else:
            try:
                c.execute(command)
                await context.send(c.fetchall())
                conn.commit()
            except Exception as e:
                await context.send(e)

    # event for people joining, making new acc
    @commands.Cog.listener()
    async def on_member_join(self, member):
        c.execute("SELECT COUNT(1) FROM cheeseballztable WHERE userid=?", (member.id,))
        if str(c.fetchone()[0]) == '0':
            defaulttime = datetime.now()
            c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly, totalgamble) VALUES (?, 0, 0, ?, ?, ?, 0)", (member.id, defaulttime, defaulttime, defaulttime))
            conn.commit()

    @commands.command(name='cheeseballz', aliases=['cb'])
    @commands.check_any(commands.has_role(658829550850932736), commands.has_guild_permissions(administrator=True))
    async def cheeseballz(self, context, operation: str = None, user: discord.User = None, amount: int = None, *, reason: str = "Not specified"):
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
                funcs.addcb(user.id, amount)
                embed = discord.Embed(title="Cheeseballz Added", color=0x00ff00)
                await self.client.logs.send(embed=fillembed(embed))
                await context.message.add_reaction(self.client.check)

            elif operation == "-" or operation == "remove":
                funcs.removecb(user.id, amount)
                embed = discord.Embed(title="Cheeseballz Removed", color=0xff0000)
                await self.client.logs.send(embed=fillembed(embed))
                await context.message.add_reaction(self.client.check)

            elif operation == "set":
                funcs.setcb(user.id, amount)
                embed = discord.Embed(title="Cheeseballz Set", color=0xffff00)
                await self.client.logs.send(embed=fillembed(embed))
                await context.message.add_reaction(self.client.check)
            else:
                await context.send(f"{context.author.mention} Command usage: `!cb <+/-/set> <@user> <amount> <reason>`")

    @commands.command(name='balance', aliases=['bal', 'profile', 'b'])
    async def balance(self, context, *, user: discord.Member = None):
        async def getbal(user):
            bal = funcs.getbal(user.id)
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (user.id,))
            upgradelevel = str(c.fetchone()[0])
            c.execute("SELECT totalgamble FROM cheeseballztable WHERE userid=?", (user.id,))
            totalgamble = str(c.fetchone()[0])
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
            embed.add_field(name="Join position", value=f"#{int(joindates.index(uniquedate)) + 1}", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="Balance", value=f"{bal} cb", inline=True)
            embed.add_field(name="Upgrade level", value=upgradelevel, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="Lifetime amount gambled", value=f"{totalgamble} cb", inline=False)
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
        prevbal = funcs.getbal(context.author.id)
        c.execute("DELETE FROM cheeseballztable WHERE userid=?", (context.author.id,))
        c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly, totalgamble) VALUES (?, 0, 0, ?, ?, ?, 0)", (context.author.id, defaulttime, defaulttime, defaulttime))
        conn.commit()
        await context.message.add_reaction(self.client.check)
        embed = discord.Embed(title="Account reset", color=0xff0000)
        embed.add_field(name="User", value=context.author.mention)
        embed.add_field(name="Previous balance", value=prevbal)
        await self.client.logs.send(embed=embed)

    @commands.command(name='shop')
    async def shop(self, context):
        balance = funcs.getbal(context.author.id)
        c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
        upgradelevel = int(c.fetchone()[0])
        embed = discord.Embed(title="Shop", description="Purchase items with !buy <number>, sell items with !sell <number>", color=0xb200b2)
        embed.set_footer(text=f"Your balance: {balance}")
        embed.add_field(name="1. Nscheeseballz Chat Permissions", value="Buy: 20,000 cb | Sell: 19,000 cb", inline=False)
        embed.add_field(name="2. DJ role", value="Buy: 5,000 cb | Sell: 4,500 cb", inline=False)
        embed.add_field(name="3. uwu role", value="Buy: 2,000 cb | Sell: 1,800 cb", inline=False)
        embed.add_field(name="4. owo role", value="Buy: 2,000 cb | Sell: 1,800 cb", inline=False)
        embed.add_field(name="5. DTRP Tokens", value="Exchange rate is 1 cb to 10 tokens.", inline=False)
        embed.add_field(name="6. Custom role", value="Buy: 30,000 cb", inline=False)
        embed.add_field(name=f"7. Increase upgrade level - Level {upgradelevel} to {upgradelevel + 1}", value="Buy: 10,000 cb", inline=False)
        await context.send(embed=embed)

    @commands.command(name='buy', aliases=['purchase'])
    async def buy(self, context, selection: int = 0):
        nscheeseballz = self.client.crdguild.get_role(674479777444265985)
        dj = self.client.crdguild.get_role(688601672766849025)
        uwu = self.client.crdguild.get_role(714783199170920508)
        owo = self.client.crdguild.get_role(725292693487485018)
        # --
        bal = funcs.getbal(context.author.id)

        async def role(role, amount):
            if bal < amount:
                await funcs.insufficientcb(context, self.client)
            else:
                funcs.removecb(context.author.id, amount)
                await context.send(f"{context.author.mention} {self.client.check} Purchase successful.")
                await context.author.add_roles(role, reason="Purchased from cheeseballz shop")
                embed = discord.Embed(title="Role Purchased", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=True)
                embed.add_field(name="Role", value=role.mention, inline=True)
                await self.client.logs.send(embed=embed)

        if selection == 1:
            await role(nscheeseballz, 20000)
        elif selection == 2:
            await role(dj, 5000)
        elif selection == 3:
            await role(uwu, 2000)
        elif selection == 4:
            await role(owo, 2000)
        elif selection == 5:
            await context.send(f"{context.author.mention} How many tokens would you like? The maximum is 150,000 tokens and the minimum is 5,000 tokens.")

            def amtcheck(m):
                return m.author == context.author and m.channel == context.channel

            amtmsg = await self.client.wait_for("message", check=amtcheck)
            try:
                tokens = int(amtmsg.content)
                cost = int(round(tokens/10))
                if tokens > 150000:
                    await context.send(f"{context.author.mention} The maximum is 150,000 tokens and the minimum is 5,000 tokens.")
                elif tokens < 5000:
                    await context.send(f"{context.author.mention} The maximum is 150,000 tokens and the minimum is 5,000 tokens.")
                else:
                    bal = funcs.getbal(context.author.id)
                    if bal < cost:
                        await funcs.insufficientcb(context, self.client)
                    else:
                        funcs.removecb(context.author.id, cost)
                        embed = discord.Embed(title="Tokens purchased", color=0xffff00)
                        embed.add_field(name="User", value=context.author.mention, inline=True)
                        embed.add_field(name="Amount", value=f"{tokens} tokens", inline=True)
                        embed.add_field(name="Cost", value=f"{cost} cb", inline=True)
                        await self.client.logs.send("<@291661685863874560>", embed=embed)
                        await context.send(f"{context.author.mention} A staff member will DM you soon for you to pick up your tokens. {cost} cheeseballz has been deducted.")
            except ValueError:
                await context.send(f"{context.author.mention} Could not parse an amount from {amtmsg.content}. Please try again.")

        elif selection == 6:
            if bal < 30000:
                await funcs.insufficientcb(context, self.client)
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
                    await context.send("Type the __HEX__ code for your role color. You can find these by Googling 'color picker'.")
                    hexmsg = await self.client.wait_for('message', check=messageresponsecheck, timeout=60)
                    hoistquestion = await context.send("Should the role be shown in the member list?")
                    await hoistquestion.add_reaction(self.client.check)
                    await hoistquestion.add_reaction(self.client.x)
                    reaction, user = await self.client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                    if reaction.emoji == self.client.check:
                        hoist = True
                    else:
                        hoist = False
                    mentionablequestion = await context.send("Should the role be mentionable by everyone?")
                    await mentionablequestion.add_reaction(self.client.check)
                    await mentionablequestion.add_reaction(self.client.x)
                    reaction, user = await self.client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                    if reaction.emoji == self.client.check:
                        mentionable = True
                    else:
                        mentionable = False
                    await context.send(f"{context.author.mention} Creating role `{rolenamemsg.content}` with hex color `{hexmsg.content}`.")
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
                        funcs.removecb(context.author.id, 30000)
                        conn.commit()
                    except ValueError:
                        await context.send(f"{context.author.mention} One or more fields had an invalid input. Try again.")
                except asyncio.TimeoutError:
                    await context.send(f"{context.author.mention} Timed out, cancelling.")
        elif selection == 7:
            if bal < 10000:
                await context.send(f"{context.author.mention} {self.client.x} Not enough cheeseballz.")
            else:
                funcs.removecb(context.author.id, 10000)
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                prev = int(c.fetchone()[0])
                upgrade = prev + 1
                c.execute("UPDATE cheeseballztable SET upgradelevel=? WHERE userid=?", (upgrade, context.author.id))
                conn.commit()
                await context.send(f"{context.author.mention} {self.client.check} Purchase successful.")
                embed = discord.Embed(title="Upgrade Level Increased", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=False)
                embed.add_field(name="Level", value=f"{prev} to {upgrade}", inline=False)
                await self.client.logs.send(embed=embed)
        else:
            await context.send(f"{context.author.mention} Select a valid item in the shop. Use `!shop` to list items.")

    @commands.command(name='sell', aliases=['refund'])
    async def sell(self, context, selection: int = 0):
        nscheeseballz = self.client.crdguild.get_role(674479777444265985)
        dj = self.client.crdguild.get_role(688601672766849025)
        uwu = self.client.crdguild.get_role(714783199170920508)
        owo = self.client.crdguild.get_role(725292693487485018)

        async def role(role, amount):
            if role in context.author.roles:
                funcs.addcb(context.author.id, amount)
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
        # elif selection == 2:
            # await role(omega, 4500)
        # elif selection == 3:
            # await role(wink, 900)
        elif selection == 4:
            await role(dj, 4500)
        # elif selection == 5:
            # await role(richman, 8100)
        elif selection == 6:
            await role(uwu, 1800)
        elif selection == 7:
            await role(owo, 1800)
        else:
            await context.send(f"{context.author.mention} Select a valid role in the shop. Use `!shop` to list items.")

    @commands.command(name='send', aliases=['pay'])
    async def send(self, context, user: discord.Member = None, amount: int = None):
        if user is None or amount is None:
            await context.send(f"{context.author.mention} Command usage: `!send <@user> <amount>`")
        else:
            if amount < 1:
                await context.send(f"{context.author.mention} {self.client.x} You must send at least one cb.")
            else:
                bal = funcs.getbal(context.author.id)
                if bal < amount:
                    await funcs.insufficientcb(context, self.client)
                else:
                    funcs.removecb(context.author.id, amount)
                    funcs.addcb(user.id, amount)
                    await context.message.add_reaction(self.client.check)
                    embed = discord.Embed(title="Cheeseballz Sent", color=0xffff00)
                    embed.add_field(name="From user", value=context.author.mention, inline=False)
                    embed.add_field(name="To user", value=user.mention, inline=True)
                    embed.add_field(name="Amount", value=f"{amount} cb", inline=True)
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
            bal = funcs.getbal(context.author.id)
            amount = random.randint(lower, upper)
            funcs.addcb(context.author.id, amount)
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
            bal = funcs.getbal(context.author.id)
            amount = random.randint(lower, upper)
            funcs.addcb(context.author.id, amount)
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
            bal = funcs.getbal(context.author.id)
            amount = random.randint(lower, upper)
            funcs.addcb(context.author.id, amount)
            c.execute("UPDATE cheeseballztable SET monthly=? WHERE userid=?", (now, context.author.id))
            conn.commit()
            await context.send(f"{context.author.mention} {self.client.check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")

    @commands.command(name='total')
    async def total(self, context):
        c.execute("SELECT SUM(cheeseballz) FROM cheeseballztable")
        total = int(c.fetchone()[0])
        cbexcluded = context.guild.get_role(726974805831843900)
        for member in cbexcluded.members:
            total = total - funcs.getbal(member.id)
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
                        userdict[userid] = funcs.getbal(userid)
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

    @commands.command(name='gambleleaderboard', aliases=['gambletop', 'gamblelb'])
    async def gambleleaderboard(self, context, page: int = 1):
        if page <= 5:
            msg = await context.send("Sorting...")
            cbexcluded = context.guild.get_role(726974805831843900)
            userdict = {}
            userlist = []
            i = 0
            while True:
                c.execute("SELECT userid FROM cheeseballztable ORDER BY totalgamble DESC LIMIT 1 OFFSET ?", (i,))
                userid = int(c.fetchone()[0])
                try:
                    member = context.guild.get_member(userid)
                    if cbexcluded in member.roles:
                        pass
                    else:
                        userdict[userid] = funcs.getbal(userid)
                        userlist.append(userid)
                except AttributeError:
                    pass
                if len(userlist) == 30:
                    break
                i = i + 1

            async def generate_leaderboard(page):
                embed = discord.Embed(title="Amount Gambled Leaderboard", description=f"Page {page}", color=0xffa500)
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
                    return user == context.message.author and (str(reaction.emoji) == '➡' or str(reaction.emoji) == '⬅')

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
    @commands.cooldown(rate=1, per=30, type=BucketType.member)
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
    @commands.has_role(564649798196658186)
    async def request(self, context, operation: str = None, user: discord.Member = None, amount: int = None, *, reason: str = None):
        if operation is None or user is None or amount is None or reason is None or amount <= 0:
            await context.send(f"{context.author.mention} Command usage: `!request <+/-> <@user> <amount> <reason>`")
        else:
            def createEmbed(color):
                embed = discord.Embed(title="Cheeseballz Request", color=color)
                embed.add_field(name="Staff member", value=context.author.mention, inline=False)
                embed.add_field(name="User", value=user.mention, inline=False)
                embed.add_field(name="Operation", value=operation, inline=False)
                embed.add_field(name="Amount", value=f"{amount} cb", inline=False)
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
                    funcs.addcb(user.id, amount)
                elif operation == '-':
                    funcs.removecb(user.id, amount)
            elif reaction.emoji == self.client.x:
                embed = createEmbed(0xff0000)
                embed.add_field(name="Denied by", value=member.mention, inline=False)
                await reqmsg.edit(embed=embed)
                await logmsg.edit(embed=embed)
                await reqmsg.clear_reactions()

    @commands.command(name='mcheeseballz', aliases=['mcb'])
    @commands.check_any(commands.has_role(658829550850932736), commands.has_guild_permissions(administrator=True))
    async def mcheeseballz(self, context, operation: str = None, amount: int = None, *, users: str = None):
        if operation is None or amount is None or users is None:
            await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
        else:
            users = re.sub("[<@!>]", "", users)
            userlist = users.split()
            for userid in userlist:
                if operation == '+':
                    funcs.addcb(userid, amount)
                elif operation == '-':
                    funcs.removecb(userid, amount)
                else:
                    await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
                    break
            embed = discord.Embed(title="Multiple cheeseballz transactions", color=0xffff00)
            embed.add_field(name="Staff", value=context.author.mention, inline=False)
            embed.add_field(name="Operation", value=operation, inline=False)
            embed.add_field(name="Amount", value=f"{amount} cb", inline=False)
            embed.add_field(name="User IDs", value=userlist, inline=False)
            await self.client.logs.send(embed=embed)
            conn.commit()
            await context.message.add_reaction(self.client.check)

    @commands.command(name='mrequest', aliases=['mreq'])
    @commands.has_role(564649798196658186)
    async def mrequest(self, context, operation: str = None, amount: int = None, *, users: str = None):
        if operation is None or amount is None or users is None:
            await context.send(f"{context.author.mention} Command usage: `!mreq <+/-> <amount> <@users>`")
        else:
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
                    embed.add_field(name="Amount", value=f"{amount} cb", inline=False)
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
                            funcs.addcb(userid, amount)
                        elif operation == '-':
                            funcs.removecb(userid, amount)
                    elif reaction.emoji == self.client.x:
                        embed = createEmbed(0xff0000)
                        embed.add_field(name="Denied by", value=member.mention, inline=False)
                        await reqmsg.edit(embed=embed)
                        await logmsg.edit(embed=embed)
                        await reqmsg.clear_reactions()


def setup(client):
    client.add_cog(Cheeseballz(client))
