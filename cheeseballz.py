#imports
import discord
import time
import random
import sys
import re
import asyncio
from datetime import datetime,timedelta
import sqlite3
from discord.ext.commands import Bot
from discord.ext import commands, tasks
from collections import OrderedDict
from discord.ext.commands.cooldowns import BucketType
import schedule

class Cheeseballz(commands.Cog):
    def __init__(self, client):
        self.client = client

        conn = sqlite3.connect('cheeseballz.db')
        c = conn.cursor()
        #--
        x = client.get_emoji(689001238141861934)
        check = client.get_emoji(688998780900737096)
        logs = client.get_channel(657112105467772929)
        requests = client.get_channel(660213957448957952)
        #---SCHEDULING FOR CLEARING DAILIES
        @tasks.loop(hours=24)
        async def clearCurrentGamble():
            c.execute("UPDATE cheeseballztable SET currentgamble=0")
            print("Current gamble reset")
            return
        #---
        crdguild = client.get_guild(528679766270935040)
        cbperms = crdguild.get_role(658829550850932736)
        #raw sql commands
        @client.command(name='cbsql')
        async def cbsql(context,*, command:str=None):
            if command == None:
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
                    await context.send(f"{context.author.mention} {x} Insufficient permissions.")

        #event for people joining, making new acc
        @client.event
        async def on_member_join(member):
            c.execute("SELECT COUNT(1) FROM cheeseballztable WHERE userid=?", (member.id,))
            if re.sub("[(),'\[\]]", "", str(c.fetchall())) == '0':
                defaulttime = "2020-01-01 00:00:00.000000"
                c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly, gamblelimit, currentgamble) VALUES (?, 0, 0, ?, ?, ?, 0, 0)", (member.id, defaulttime, defaulttime, defaulttime))
                conn.commit()
        #cheeseballz add, remove, set
        @client.command(name='cheeseballz',
                        aliases=['cb'])
        async def cheeseballz(context, operation:str=None, user:discord.Member=None, amount:int=None,*, reason:str="Not specified"):
            if cbperms in context.author.roles or context.author.guild_permissions.adminstrator:
                if operation == None or user == None or amount == None:
                    await context.send(f"{context.author.mention} Command usage: `!cb <+/-/set> <@user> <amount> <reason>`")
                else:
                    async def process(action, color):
                        c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                        bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                        if operation == "+":
                            if bankbal < amount:
                                await context.send(f"{context.author.mention} The bank does not have enough cheeseballz to process the transaction.")
                            else:
                                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal - amount,))
                                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbal, user.id))
                                embed = discord.Embed(title=f"Cheeseballz {action}", color=color)
                                embed.add_field(name="Staff", value=context.author.mention, inline=False)
                                embed.add_field(name="User", value=user.mention, inline=True)
                                embed.add_field(name="Amount", value=amount, inline=False)
                                embed.add_field(name="New Balance", value=newbal, inline=False)
                                embed.add_field(name="Reason", value=reason, inline=False)
                                await logs.send(embed=embed)
                                await context.message.add_reaction(check)
                        elif operation == "-":
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbal, user.id))
                            embed = discord.Embed(title=f"Cheeseballz {action}", color=color)
                            embed.add_field(name="Staff", value=context.author.mention, inline=False)
                            embed.add_field(name="User", value=user.mention, inline=True)
                            embed.add_field(name="Amount", value=amount, inline=False)
                            embed.add_field(name="New Balance", value=newbal, inline=False)
                            embed.add_field(name="Reason", value=reason, inline=False)
                            await logs.send(embed=embed)
                            await context.message.add_reaction(check)
                        conn.commit()
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (user.id,))
                    prevbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    if operation == "+":
                        newbal = prevbal + amount
                        await process("Added", 0x00ff00)
                    elif operation == "-":
                        newbal = prevbal - amount
                        await process("Removed", 0xff0000)
                    elif operation == "set":
                        newbal = amount
                        await process("Set", 0xffff00)
                    else:
                        await context.send(f"{context.author.mention} Command usage: `!cb <+/-/set> <@user> <amount> <reason>`")
            else:
                await context.send(f"{context.author.mention} {x} Insufficient permissions.")

        #balance
        @client.command(name='balance',
                        aliases=['bal','profile'])
        async def balance(context,*, user:discord.Member=None):
            async def getbal(user):
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (user.id,))
                bal = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (user.id,))
                upgradelevel = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                c.execute("SELECT gamblelimit FROM cheeseballztable WHERE userid=?", (user.id,))
                gamblelimit = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (user.id,))
                currentgamble = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                c.execute("SELECT about FROM cheeseballztable WHERE userid=?", (user.id,))
                about = re.sub("[(),\[\]]", "", str(c.fetchall()))
                c.execute("SELECT daily FROM cheeseballztable WHERE userid=?", (user.id,))
                daily = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
                c.execute("SELECT weekly FROM cheeseballztable WHERE userid=?", (user.id,))
                weekly = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
                c.execute("SELECT monthly FROM cheeseballztable WHERE userid=?", (user.id,))
                monthly = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
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
                embed.add_field(name="Gambling limit", value=gamblelimit, inline=True)
                embed.add_field(name="Amount gambled today", value=currentgamble, inline=True)
                embed.add_field(name="\u200b", value="\u200b", inline=True)
                embed.add_field(name="Time until next !daily", value=dailytimeleft, inline=False)
                embed.add_field(name="Time until next !weekly", value=weeklytimeleft, inline=False)
                embed.add_field(name="Time until next !monthly", value=monthlytimeleft, inline=False)
                embed.add_field(name="About", value=about, inline=False)
                await context.send(embed=embed)
            if user == None:
                await getbal(context.author)
            else:
                await getbal(user)

        #reset account
        @client.command(name='resetaccount',
                        aliases=['resetacc'])
        async def resetaccount(context):
            defaulttime = "2020-01-01 00:00:00.000000"
            c.execute("DELETE FROM cheeseballztable WHERE userid=?", (context.author.id,))
            c.execute("INSERT INTO cheeseballztable(userid, cheeseballz, upgradelevel, daily, weekly, monthly) VALUES (?, 0, 0, ?, ?, ?)", (context.author.id, defaulttime, defaulttime, defaulttime))
            conn.commit()
            await context.message.add_reaction(check)
            embed = discord.Embed(title="Account reset", color=0xff0000)
            embed.add_field(name="User", value=context.author.mention)
            await logs.send(embed=embed)

        #shop
        @client.command(name='shop')
        async def shop(context):
            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
            balance = re.sub("[(),'\[\]]", "", str(c.fetchall()))
            c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
            upgradelevel = re.sub("[(),'\[\]]", "", str(c.fetchall()))
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
            embed.add_field(name=f"9. Increase upgrade level - Level {upgradelevel} to {int(upgradelevel) + 1}", value="Buy: 10,000 cb", inline=False)
            await context.send(embed=embed)

        #buying items
        @client.command(name='buy',
                        aliases=['purchase'])
        async def buy(context, selection:int=0):
            nscheeseballz = crdguild.get_role(674479777444265985)
            omega = crdguild.get_role(674478322687672351)
            wink = crdguild.get_role(674481196239028235)
            dj = crdguild.get_role(688601672766849025)
            richman = crdguild.get_role(704053604172038184)
            uwu = crdguild.get_role(714783199170920508)
            owo = crdguild.get_role(725292693487485018)
            #--
            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
            bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            async def role(role, amount):
                if bal < amount:
                    await context.send(f"{context.author.mention} {x} Not enough cheeseballz. You currently have {bal} cheeseballz.")
                else:
                    newbal = bal - amount
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbal, context.author.id))
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                    conn.commit()
                    await context.send(f"{context.author.mention} {check} Purchase successful.")
                    await context.author.add_roles(role, reason="Purchased from cheeseballz shop")
                    embed = discord.Embed(title="Role Purchased", color=0x00ff00)
                    embed.add_field(name="User", value=context.author.mention, inline=False)
                    embed.add_field(name="Role", value=role.mention, inline=False)
                    await logs.send(embed=embed)
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
                    await context.send(f"{context.author.mention} Not enough cheeseballz. You currently have {bal} cheeseballz.")
                else:
                    checkmsg = await context.send(f"""{context.author.mention} Purchasing a custom role for 30,000 cb.
- You have 60 seconds to respond to each question.
- You may cancel by ignoring the question for 60 seconds.
- I suggest making the role you want in your own server first, to ensure names and hex color codes work.
Click the checkmark to continue once you're ready.""")
                    await checkmsg.add_reaction(check)
                    def readycheck(reaction, member):
                        return reaction.emoji == check and member == context.author
                    def messageresponsecheck(m):
                        return m.author == context.author and m.channel == context.channel
                    def reactionresponsecheck(reaction, member):
                        return (reaction.emoji == check or reaction.emoji == x) and member == context.author and reaction.message.channel == context.channel
                    try:
                        await client.wait_for('reaction_add', check=readycheck, timeout=300)
                        await context.send("Type the new role name.")
                        rolenamemsg = await client.wait_for('message', check=messageresponsecheck, timeout=60)
                        await context.send("Type the __HEX__ code for your role color. You can find these by Googling 'color picker'.")
                        hexmsg = await client.wait_for('message', check=messageresponsecheck, timeout=60)
                        hoistquestion = await context.send("Should the role be shown in the member list?")
                        await hoistquestion.add_reaction(check)
                        await hoistquestion.add_reaction(x)
                        reaction, user = await client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                        if reaction.emoji == check:
                            hoist = True
                        elif reaction.emoji == x:
                            hoist = False
                        mentionablequestion = await context.send("Should the role be mentionable by everyone?")
                        await mentionablequestion.add_reaction(check)
                        await mentionablequestion.add_reaction(x)
                        reaction, user = await client.wait_for('reaction_add', check=reactionresponsecheck, timeout=60)
                        if reaction.emoji == check:
                            mentionable = True
                        elif reaction.emoji == x:
                            mentionable = False
                        await context.send(f"{context.author.mention} Creating role `{rolenamemsg.content}` with hex color `{hexmsg.content}`.")
                        try:
                            if '#' in hexmsg.content:
                                fixedhex = re.sub("[#]", "", hexmsg.content)
                            else:
                                fixedhex = hexmsg.content
                            hexcode = discord.Color(int(fixedhex, 16))
                            newrole = await context.guild.create_role(name=rolenamemsg.content, color=hexcode, hoist=hoist, mentionable=mentionable, reason=f"Created by {context.author.id}, custom role from shop.")
                            await newrole.edit(position=12)
                            await context.author.add_roles(newrole)
                            await context.send(f"{context.author.mention} Role created and assigned to you.")
                            embed = discord.Embed(name="Custom role created", color=0xffff00)
                            embed.add_field(name="User", value=context.author.mention, inline=False)
                            embed.add_field(name="Role name", value=rolenamemsg.content, inline=False)
                            embed.add_field(name="Role color", value=hexmsg.content, inline=False)
                            await logs.send(embed=embed)
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal-30000, context.author.id))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + 30000,))
                            conn.commit()
                        except:
                            await context.send(f"{context.author.mention} One or more fields had an invalid input. Try again.")
                    except asyncio.TimeoutError:
                        await context.send(f"{context.author.mention} Timed out, cancelling.")
            elif selection == 9:
                newbal = bal - 10000
                if newbal < 0:
                    await context.send(f"{context.author.mention} {x} Not enough cheeseballz.")
                else:
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbal, context.author.id))
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + 10000,))
                    c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                    upgrade = int(re.sub("[(),'\[\]]", "", str(c.fetchall()))) + 1
                    c.execute("UPDATE cheeseballztable SET upgradelevel=? WHERE userid=?", (upgrade, context.author.id))
                    conn.commit()
                    await context.send(f"{context.author.mention} {check} Purchase successful.")
                    embed = discord.Embed(title="Upgrade Level Increased", color=0x00ff00)
                    embed.add_field(name="User", value=context.author.mention, inline=False)
                    embed.add_field(name="New Upgrade Level", value=upgrade, inline=False)
                    await logs.send(embed=embed)
            else:
                await context.send(f"{context.author.mention} Select a valid item in the shop. Use `!shop` to list items.")
        #selling/refunding
        @client.command(name='sell',
                        aliases=['refund'])
        async def sell(context, selection:int=0):
            nscheeseballz = crdguild.get_role(674479777444265985)
            omega = crdguild.get_role(674478322687672351)
            wink = crdguild.get_role(674481196239028235)
            dj = crdguild.get_role(688601672766849025)
            richman = crdguild.get_role(704053604172038184)
            uwu = crdguild.get_role(714783199170920508)
            owo = crdguild.get_role(725292693487485018)
            #--
            async def role(role, amount):
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                if role in context.author.roles:
                    newbal = bal + amount
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbal, context.author.id))
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal - amount,))
                    conn.commit()
                    await context.author.remove_roles(role, reason="Sold to cheeseballz shop")
                    await context.send(f"{context.author.mention} {check} Refund successful. Received {amount} cheeseballz.")
                    embed = discord.Embed(title="Role sold", color=0x00ff00)
                    embed.add_field(name="User", value=context.author.mention, inline=False)
                    embed.add_field(name="Role", value=role.mention, inline=False)
                    await logs.send(embed=embed)
                else:
                    await context.send(f"{context.author.mention} {x} You don't have the specified role to sell.")
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
                await context.send(f"{context.author.mention} Select a valid role in the shop. Use `!shop` to list items.")

        #sending cb
        @client.command(name='send',
                        aliases=['pay'])
        async def send(context, user:discord.Member=None, amount:int=None):
            if user == None or amount == None:
                await context.send(f"{context.author.mention} Command usage: `!send <@user> <amount>`")
            else:
                if amount < 1:
                    await context.send(f"{context.author.mention} {x} You must send at least one cb.")
                else:
                    if amount <= 5000 or cbperms in context.author.roles:
                        c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                        bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                        if bal < amount:
                            await context.send(
                                f"{context.author.mention} {x} Not enough cheeseballz. You currently have {bal} cheeseballz.")
                        else:
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?",
                                      (bal - amount, context.author.id,))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (user.id,))
                            userbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?",
                                      (userbal + amount, user.id))
                            conn.commit()
                            await context.message.add_reaction(check)
                            embed = discord.Embed(title="Cheeseballz Sent", color=0xffff00)
                            embed.add_field(name="From user", value=context.author.mention, inline=False)
                            embed.add_field(name="Sender's new balance", value=bal - amount, inline=False)
                            embed.add_field(name="To user", value=user.mention, inline=False)
                            embed.add_field(name="Receiver's new balance", value=userbal + amount, inline=False)
                            embed.add_field(name="Amount", value=amount, inline=False)
                            await logs.send(embed=embed)
                    else:
                        await context.send(f"{context.author.mention} You may send a maximum of 5,000 cb at a time. Contact someone with the Cheeseballz Permissions role to bypass this.")
        #daily
        @client.command(name='daily',
                        aliases=['d'])
        async def daily(context):
            c.execute("SELECT daily FROM cheeseballztable WHERE userid=?", (context.author.id,))
            daily = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if daily + timedelta(hours=23) > now:
                dhours = (daily + timedelta(hours=23) - now).seconds // 3600
                dminutes = (daily + timedelta(hours=23) - now).seconds // 60 % 60
                await context.send(f"{context.author.mention} {x} Your daily cheeseballz resets in **{dhours} hours and {dminutes} minutes.**")
            else:
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                upgradelevel = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                lower = 100 + (upgradelevel * 100)
                upper = 200 + (upgradelevel * 100)
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                amount = random.randint(lower, upper)
                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + amount, context.author.id))
                c.execute("UPDATE cheeseballztable SET daily=? WHERE userid=?", (now, context.author.id))
                conn.commit()
                await context.send(f"{context.author.mention} {check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")
                embed = discord.Embed(title="Daily cheeseballz collected", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=True)
                embed.add_field(name="Amount", value=amount, inline=True)
                embed.add_field(name="New balance", value=bal+amount, inline=True)
                await logs.send(embed=embed)

        #weekly
        @client.command(name='weekly',
                        aliases=['w'])
        async def weekly(context):
            c.execute("SELECT weekly FROM cheeseballztable WHERE userid=?", (context.author.id,))
            weekly = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if weekly + timedelta(days=6, hours=23) > now:
                wdays = (weekly + timedelta(days=6, hours=23) - now).days
                whours = (weekly + timedelta(days=6, hours=23) - now).seconds // 3600
                wminutes = (weekly + timedelta(days=6, hours=23) - now).seconds // 60 % 60
                await context.send(f"{context.author.mention} {x} Your weekly cheeseballz resets in **{wdays} days, {whours} hours, and {wminutes} minutes.**")
            else:
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                upgradelevel = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                lower = 600 + (upgradelevel * 200)
                upper = 800 + (upgradelevel * 200)
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                amount = random.randint(lower, upper)
                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + amount, context.author.id))
                c.execute("UPDATE cheeseballztable SET weekly=? WHERE userid=?", (now, context.author.id))
                conn.commit()
                await context.send(f"{context.author.mention} {check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")
                embed = discord.Embed(title="Weekly cheeseballz collected", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=True)
                embed.add_field(name="Amount", value=amount, inline=True)
                embed.add_field(name="New balance", value=bal+amount, inline=True)
                await logs.send(embed=embed)

        #monthly
        @client.command(name='monthly',
                        aliases=['m'])
        async def monthly(context):
            c.execute("SELECT monthly FROM cheeseballztable WHERE userid=?", (context.author.id,))
            monthly = datetime.strptime(re.sub("[(),'\[\]]", "", str(c.fetchall())), '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if monthly + timedelta(days=29, hours=23) > now:
                mdays = (monthly + timedelta(days=29, hours=23) - now).days
                mhours = (monthly + timedelta(days=29, hours=23) - now).seconds // 3600
                mminutes = (monthly + timedelta(days=29, hours=23) - now).seconds // 60 % 60
                await context.send(f"{context.author.mention} {x} Your monthly cheeseballz resets in **{mdays} days, {mhours} hours, and {mminutes} minutes.**")
            else:
                c.execute("SELECT upgradelevel FROM cheeseballztable WHERE userid=?", (context.author.id,))
                upgradelevel = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                lower = 1500 + (upgradelevel * 500)
                upper = 2000 + (upgradelevel * 500)
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                amount = random.randint(lower, upper)
                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + amount, context.author.id))
                c.execute("UPDATE cheeseballztable SET monthly=? WHERE userid=?", (now, context.author.id))
                conn.commit()
                await context.send(f"{context.author.mention} {check} Collected {amount} cheeseballz. You now have {bal + amount} cheeseballz.")
                embed = discord.Embed(title="Monthly cheeseballz collected", color=0x00ff00)
                embed.add_field(name="User", value=context.author.mention, inline=True)
                embed.add_field(name="Amount", value=amount, inline=True)
                embed.add_field(name="New balance", value=bal+amount, inline=True)
                await logs.send(embed=embed)

        #total amount of cb in database
        @client.command(name='total')
        async def total(context):
            c.execute("SELECT SUM(cheeseballz) FROM cheeseballztable")
            total = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            cbexcluded = context.guild.get_role(726974805831843900)
            for member in cbexcluded.members:
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (member.id,))
                total = total - int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            await context.send(f"The guild currently has {total} cheeseballz stored.")

        #leaderboard system
        @client.command(name='leaderboard',
                        aliases=['top','lb'])
        async def leaderboard(context, page:int=1):
            if page <= 5:
                msg = await context.send("Sorting...")
                cbexcluded = context.guild.get_role(726974805831843900)
                extra = len(cbexcluded.members)
                userdict = {}
                userlist = []
                i = 0
                while True:
                    c.execute("SELECT userid FROM cheeseballztable ORDER BY cheeseballz DESC LIMIT 1 OFFSET ?", (i,))
                    userid = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    try:
                        member = context.guild.get_member(userid)
                        if cbexcluded in member.roles:
                            pass
                        else:
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
                            userdict[userid] = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                            userlist.append(userid)
                    except AttributeError as e:
                        pass
                    if len(userlist) == 30:
                        break
                    i = i + 1
                async def generate_leaderboard(page):
                    embed = discord.Embed(title="Cheeseballz Leaderboard", description=f"Page {page}", color=0xffa500)
                    upper = page * 10
                    lower = upper - 10
                    for i in range(lower, upper):
                        embed.add_field(name="-------", value=f"{i + 1}. <@{userlist[i]}> - {userdict[userlist[i]]} cheeseballz", inline=False)
                    await msg.edit(content=None, embed=embed)
                while True:
                    await generate_leaderboard(page)
                    if page == 1:
                        await msg.add_reaction(u"\U000027a1") #arrow pointing right
                    elif page == 3:
                        await msg.add_reaction(u"\U00002b05") #arrow pointing left
                    else:
                        await msg.add_reaction(u"\U00002b05") #arrow pointing left
                        await msg.add_reaction(u"\U000027a1") #arrow pointing right
                    def check(reaction, user):
                        return user == context.message.author and (str(reaction.emoji) == '➡' or str(reaction.emoji) == '⬅')
                    try:
                        reaction, user = await client.wait_for('reaction_add', timeout=10, check=check)
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

        #setabout
        @client.command(name='setabout')
        async def setabout(context,*,about:str=None):
            if about == None:
                await context.send(f"{context.author.mention} Command usage: `!setabout <about>`")
            else:
                if len(about) > 500:
                    await context.send(f"{context.author.mention} {x} Too many characters. The limit is 500; you currently have {len(about)}.")
                else:
                    c.execute("UPDATE cheeseballztable SET about=? WHERE userid=?", (about, context.author.id))
                    conn.commit()
                    embed = discord.Embed(title="About Changed", color=0xc6c6c6)
                    embed.add_field(name="User", value=context.author.mention, inline=True)
                    embed.add_field(name="New content", value=about, inline=True)
                    await logs.send(embed=embed)
                    await context.message.add_reaction(check)

        #adding requests
        @client.command(name='request',
                        aliases=['req'])
        async def request(context, operation:str=None, user:discord.Member=None, amount:int=None,*, reason:str=None):
            if operation == None or user == None or amount == None or reason == None or amount <= 0:
                await context.send(f"{context.author.mention} Command usage: `!request <+/-> <@user> <amount> <reason>`")
            else:
                staff = context.guild.get_role(564649798196658186)
                if staff in context.author.roles:
                    def createEmbed(color):
                        embed = discord.Embed(title="Cheeseballz Request", color=color)
                        embed.add_field(name="Staff member", value=context.author.mention, inline=False)
                        embed.add_field(name="User", value=user.mention, inline=False)
                        embed.add_field(name="Operation", value=operation, inline=False)
                        embed.add_field(name="Amount", value=amount, inline=False)
                        embed.add_field(name="Reason", value=reason, inline=False)
                        return embed
                    embed = createEmbed(0x6c6c6c)
                    reqmsg = await requests.send(embed=embed)
                    logmsg = await logs.send(embed=embed)
                    await reqmsg.add_reaction(check)
                    await reqmsg.add_reaction(x)
                    await context.message.add_reaction(check)
                    def reactioncheck(reaction, member):
                        return (reaction.emoji == check or reaction.emoji == x) and reaction.message.id == reqmsg.id and cbperms in member.roles
                    reaction, member = await client.wait_for('reaction_add', check=reactioncheck)
                    if reaction.emoji == check:
                        embed = createEmbed(0x00ff00)
                        embed.add_field(name="Accepted by", value=member.mention, inline=False)
                        await reqmsg.edit(embed=embed)
                        await logmsg.edit(embed=embed)
                        await reqmsg.clear_reactions()
                        c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (user.id,))
                        bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                        if operation == '+':
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + amount, user.id))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal - amount,))
                        elif operation == '-':
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal - amount, user.id))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                        conn.commit()
                    elif reaction.emoji == x:
                        embed = createEmbed(0xff0000)
                        embed.add_field(name="Denied by", value=member.mention, inline=False)
                        await reqmsg.edit(embed=embed)
                        await logmsg.edit(embed=embed)
                        await reqmsg.clear_reactions()
                else:
                    await context.send(f"{context.author.mention} {x} Insufficient permissions.")
                    
        #slots thing
        @client.command(name="slots")
        @commands.cooldown(rate=1, per=4 ,type=BucketType.member)
        async def slots(context, amount:int=None):
            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
            bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
            currentgamble = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT gamblelimit FROM cheeseballztable WHERE userid=?", (context.author.id,))
            gamblelimit = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            if gamblelimit == 0:
                gamblelimit = 999999999999999999999999999999999
            if amount == None:
                await context.send(f"{context.author.mention} Command usage: `!slots <amount>`")
            elif amount < 10:
                await context.send(f"{context.author.mention} You must bet a minimum of 10 cheeseballz. You currently have {bal} cheeseballz.")
            elif (currentgamble + amount) > gamblelimit:
                await context.send(f"{context.author.mention} The current bet would make you go over your gambling limit of {gamblelimit} cheeseballz.")
            else:
                if bal < amount:
                    await context.send(f"{context.author.mention} {x} Not enough cheeseballz. You currently have {bal} cheeseballz.")
                else:
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal - amount, context.author.id,))
                    
                    c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                    conn.commit()
                    roll = ['empty']
                    for i in range(18):
                        roll.append(random.choice([':strawberry:',':pear:',':tangerine:',':grapes:',':watermelon:']))
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
                        await context.send(f"{context.author.mention} Congrats! Received {amount*12} cheeseballz back.")
                        winnings = amount * 12
                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + winnings, context.author.id,))
                        conn.commit()
                    else:
                        await context.send(f"{context.author.mention} Sorry, try again.")
                    
        #russian roulette
        @client.command(name='russianroulette',
                        aliases=['rr','russian-roulette'])
        async def russianroulette(context, operation:str=None, gameid:int=None, amount:int=None):
            if operation == None or gameid == None:
                await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")
            else:
                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
                balance = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                async def startgame(gameid, amount):
                    c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                    if re.sub("[(),'\[\]]", "", str(c.fetchall())) == 'None':
                        await context.send(f"{context.author.mention} Two or more players are required to start.")
                    else:
                        c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                        player1 = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                        if str(context.author.id) == player1:
                            c.execute("UPDATE russianroulette SET started=1 WHERE gameid=?", (gameid,))
                            await context.send(f"{context.author.mention} Starting game {gameid}.")
                            players = []
                            toRemove = []
                            ended = False
                            for i in range(1,7):
                                playernum = ('player' + str(i))
                                c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?", (gameid,))
                                player = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                if player != 'None':
                                    players.append(player)
                            originalPlayers = len(players)
                            #functions
                            def refreshchamber():
                                functionchamber = []
                                for i in range(len(players)):
                                    choice = random.randint(0,1)
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
                            #actual
                            while ended == False:
                                chamber = refreshchamber()
                                for i in range(len(players)):
                                    pending = await fire(i)
                                    if pending != None:
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
                                        bet = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                        toAdd = int(bet) * originalPlayers
                                        c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (int(players[0]),))
                                        balance = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                        pendingAdd = int(balance) + toAdd
                                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (pendingAdd, int(players[0])))
                                        await context.send(f"{toAdd} cheeseballz has been deposited to <@{players[0]}>'s account.")
                                        embed = discord.Embed(title="Won Russian Roulette", color=0x00ff00)
                                        embed.add_field(name="User", value=f"<@{players[0]}>", inline=True)
                                        embed.add_field(name="Amount", value=toAdd, inline=True)
                                        await logs.send(embed=embed)
                                        c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                        conn.commit()
                                        ended = True
                        else:
                            if player1 == '':
                                await context.send(f"{context.author.mention} The specified game does not exist.")
                            else:
                                await context.send(f"{context.author.mention} Only the host can start the game.")
                if operation == 'new':
                    if amount == None:
                        await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")
                    else:
                        c.execute("SELECT COUNT(1) FROM russianroulette WHERE gameid=?", (gameid,))
                        if re.sub("[(),'\[\]]", "", str(c.fetchall())) != '0':
                            await context.send(f"{context.author.mention} A game with this ID already exists. Pick a different ID.")
                        else:
                            if amount <= 0:
                                await context.send(f"{context.author.mention} You must bet more than 0 cheeseballz. You currently have {balance} cheeseballz.")
                            else:
                                if amount > int(balance):
                                        await context.send(f"{context.author.mention} Insufficient cheeseballz to make that bet. You currently have {balance} cheeseballz.")
                                else:
                                    c.execute("INSERT INTO russianroulette(gameid, bet, player1, started) VALUES (?, ?, ?, 0)", (gameid, amount, context.author.id))
                                    newbalance = int(balance) - amount
                                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbalance, context.author.id,))
                                    embed = discord.Embed(title="Started Russian Roulette", color=0x0000ff)
                                    embed.add_field(name="User", value=context.author.mention, inline=True)
                                    embed.add_field(name="Amount", value=amount, inline=True)
                                    await logs.send(embed=embed)
                                    conn.commit()
                                    embed = discord.Embed(title="Russian Roulette", color=0xffa500)
                                    embed.add_field(name="Game ID", value=gameid, inline=False)
                                    embed.add_field(name="Bet", value=amount, inline=False)
                                    embed.add_field(name="Player 1", value=context.author.mention)
                                    await context.send(embed=embed)
                                    await asyncio.sleep(30)
                                    c.execute("SELECT started FROM russianroulette WHERE gameid=?", (gameid,))
                                    if re.sub("[(),'\[\]]", "", str(c.fetchall())) == '0':
                                        await context.send(f"{context.author.mention} 30 second timeout passed. Automatically starting game {gameid}.")
                                        c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                                        if re.sub("[(),'\[\]]", "", str(c.fetchall())) == 'None':
                                            await context.send(f"{context.author.mention} Not enough players to start game automatically. Deleting game, refunding {amount} cheeseballz.")
                                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (int(balance), context.author.id))
                                            c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                            embed = discord.Embed(title="Cancelled Russian Roulette", color=0x00ff00)
                                            embed.add_field(name="User", value=context.author.mention, inline=True)
                                            embed.add_field(name="Amount", value=amount, inline=True)
                                            await logs.send(embed=embed)
                                            conn.commit()
                                        else:
                                            await startgame(gameid, amount)
                elif operation == 'join':
                    if gameid == 0:
                        await context.send(f"{context.author.mention} Specify a valid game id.")
                    else:
                        c.execute("SELECT started FROM russianroulette WHERE gameid=?", (gameid,))
                        if re.sub("[(),'\[\]]", "", str(c.fetchall())) == '1':
                            await context.send(f"{context.author.mention} This game has already started.")
                        else:
                            c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                            if re.sub("[(),'\[\]]", "", str(c.fetchall())) == context.author.id:
                                await context.send(f"{context.author.mention} You are already in this game.")
                            else:
                                c.execute("SELECT player6 FROM russianroulette WHERE gameid=?", (gameid,))
                                if re.sub("[(),'\[\]]", "", str(c.fetchall())) != 'None':
                                    c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                                    if re.sub("[(),'\[\]]", "", str(c.fetchall())) != 'None':
                                        await context.send(f"{context.author.mention} Specify a valid game id.")
                                    else:
                                        await context.send(f"{context.author.mention} This game is already full.")
                                else:
                                    c.execute("SELECT bet FROM russianroulette WHERE gameid=?", (gameid,))
                                    amount = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                    if int(amount) > int(balance):
                                        await context.send(f"{context.author.mention} Insufficient cheeseballz to make that bet. You currently have {balance} cheeseballz.")
                                    else:
                                        async def join(playernum):
                                            c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?", (gameid,))
                                            if re.sub("[(),'\[\]]", "", str(c.fetchall())) == 'None':
                                                c.execute(f"UPDATE russianroulette SET {playernum}=? WHERE gameid=?", (context.author.id, gameid))
                                                newbalance = int(balance) - int(amount)
                                                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (newbalance, context.author.id,))
                                                embed = discord.Embed(title="Joined Russian Roulette", color=0x0000ff)
                                                embed.add_field(name="User", value=context.author.mention, inline=True)
                                                embed.add_field(name="Amount", value=amount, inline=True)
                                                await logs.send(embed=embed)
                                                conn.commit()
                                                await context.send(f"{context.author.mention} Joined game {gameid}, betting {amount} cheeseballz.")
                                                return True
                                            else:
                                                return False
                                        for i in range(2, 7):
                                            playernum = ('player' + str(i))
                                            result = await join(playernum)
                                            if result == True:
                                                break
                                        embed = discord.Embed(title="Russian Roulette", color=0xffa500)
                                        embed.add_field(name="Game ID", value=gameid, inline=False)
                                        #bet
                                        c.execute("SELECT bet FROM russianroulette WHERE gameid=?", (gameid,))
                                        newbet = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                        embed.add_field(name="Bet", value=amount, inline=False)
                                        #first player---
                                        c.execute("SELECT player1 FROM russianroulette WHERE gameid=?", (gameid,))
                                        player1 = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                        embed.add_field(name="Player 1", value=f"<@{player1}>", inline=False)
                                        #second player---
                                        c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                                        player2 = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                        embed.add_field(name="Player 2", value=f"<@{player2}>", inline=False)
                                        #check for third-sixth
                                        for i in range(3, 7):
                                            c.execute(f"SELECT {('player' + str(i))} FROM russianroulette WHERE gameid=?", (gameid,))
                                            playernum = re.sub("[(),'\[\]]", "", str(c.fetchall()))
                                            if playernum != 'None':
                                                embed.add_field(name=f"Player {i}", value=f"<@{playernum}>", inline=False)
                                        await context.send(embed=embed)
                elif operation == 'start':
                    await startgame(gameid,amount)
                else:
                    await context.send(f"{context.author.mention} Command usage: `!rr <new/join/start> <gameid> <amount>`")

        @client.command(name='double',
                        aliases=['dub','doub'])
        @commands.cooldown(rate=1, per=2, type=BucketType.member)
        async def double(context, amount:int=None):
            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
            bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
            currentgamble = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT gamblelimit FROM cheeseballztable WHERE userid=?", (context.author.id,))
            gamblelimit = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            if gamblelimit == 0:
                gamblelimit = 999999999999999999999999999999999
            if amount == None:
                await context.send(f"{context.author.mention} Command usage: `!double <amount>`")
            elif amount > bal:
                await context.send(f"{context.author.mention} Insufficient cheeseballz to make that bet. You currently have {bal} cheeseballz.")
            elif amount < 1:
                await context.send(f"{context.author.mention} You must bet at least one cheeseballz.")
            elif (currentgamble + amount) > gamblelimit:
                await context.send(f"{context.author.mention} The current bet would make you go over your gambling limit of {gamblelimit} cheeseballz.")
            else:
                c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal-amount, context.author.id))
                if random.choice([True, False]) == True:
                    await context.send(f"{context.author.mention} Congrats! Received {amount*2} cheeseballz back.")
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal+amount, context.author.id))
                else:
                    await context.send(f"{context.author.mention} Sorry, try again.")
                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                conn.commit()

        @client.command(name='mcheeseballz',
                        aliases=['mcb'])
        async def mcheeseballz(context, operation:str=None, amount:int=None,*, users:str=None):
            if operation == None or amount == None or users == None:
                await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
            else:
                if cbperms in context.author.roles or context.author.guild_permissions.administrator:
                    users = re.sub("[<@!>]", "", users)
                    userlist = users.split()
                    for userid in userlist:
                        c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
                        bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                        if operation == '+':
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal+amount, userid))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal - amount,))
                        elif operation == '-':
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal-amount, userid))
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                        else:
                            await context.send(f"{context.author.mention} Command usage: `!mcb <+/-> <amount> <@users>`")
                            break
                    embed = discord.Embed(title="Multiple cheeseballz transactions", color=0xffff00)
                    embed.add_field(name="Staff", value=context.author.mention, inline=False)
                    embed.add_field(name="Operation", value=operation, inline=False)
                    embed.add_field(name="Amount", value=amount, inline=False)
                    embed.add_field(name="User IDs", value=userlist, inline=False)
                    await logs.send(embed=embed)
                    conn.commit()
                    await context.message.add_reaction(check)
                else:
                    await context.send(f"{context.author.mention} {x} Insufficient permissions.")

        @client.command(name='mrequest',
                        aliases=['mreq'])
        async def mrequest(context, operation:str=None, amount:int=None,*, users:str=None):
            if operation == None or amount == None or users == None:
                await context.send(f"{context.author.mention} Command usage: `!mreq <+/-> <amount> <@users>`")
            else:
                staff = context.guild.get_role(564649798196658186)
                if staff in context.author.roles:
                    await context.send(f"{context.author.mention} Reason?")
                    def messagecheck(m):
                        return m.author == context.author and m.channel == context.channel
                    try:
                        reason = await client.wait_for('message', check=messagecheck, timeout=30)
                    except asyncio.TimeoutError:
                        reason = None
                    if reason == None:
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
                            reqmsg = await requests.send(embed=embed)
                            logmsg = await logs.send(embed=embed)
                            await reqmsg.add_reaction(check)
                            await reqmsg.add_reaction(x)
                            reqmsgs.append(reqmsg)
                        await context.message.add_reaction(check)
                        for reqmsg in reqmsgs:
                            def reactioncheck(reaction, member):
                                return (reaction.emoji == check or reaction.emoji == x) and reaction.message.id == reqmsg.id and cbperms in member.roles
                            reaction, member = await client.wait_for('reaction_add', check=reactioncheck)
                            if reaction.emoji == check:
                                embed = createEmbed(0x00ff00)
                                embed.add_field(name="Accepted by", value=member.mention, inline=False)
                                await reqmsg.edit(embed=embed)
                                await logmsg.edit(embed=embed)
                                await reqmsg.clear_reactions()
                                c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
                                bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                                if operation == '+':
                                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal + amount, userid))
                                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal - amount,))
                                elif operation == '-':
                                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal - amount, userid))
                                    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                                    bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                                    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                                conn.commit()
                            elif reaction.emoji == x:
                                embed = createEmbed(0xff0000)
                                embed.add_field(name="Denied by", value=member.mention, inline=False)
                                await reqmsg.edit(embed=embed)
                                await logmsg.edit(embed=embed)
                                await reqmsg.clear_reactions()
                else:
                    await context.send(f"{context.author.mention} {x} Insufficient permissions.")
        @client.command(name='blackjack',
                        aliases=['bj'])
        @commands.cooldown(rate=2, per=20 ,type=BucketType.member)
        async def blackjack(context, amount:int=None):
            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (context.author.id,))
            bal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT currentgamble FROM cheeseballztable WHERE userid=?", (context.author.id,))
            currentgamble = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            c.execute("SELECT gamblelimit FROM cheeseballztable WHERE userid=?", (context.author.id,))
            gamblelimit = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
            if gamblelimit == 0:
                gamblelimit = 999999999999999999999999999999999
            if amount == None:
                await context.send(f"{context.author.mention} Command usage: `!blackjack <amount>`")
            elif amount < 50:
                await context.send(f"{context.author.mention} You must bet at least 50 cheeseballz.")
            elif bal < amount:
                await context.send(f"{context.author.mention} Insufficient cheeseballz to make that bet. You currently have {bal} cheeseballz.")
            elif (currentgamble + amount) > gamblelimit:
                await context.send(f"{context.author.mention} The current bet would make you go over your gambling limit of {gamblelimit} cheeseballz.")
            else:
                c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal-amount, context.author.id))
                c.execute("UPDATE cheeseballztable SET currentgamble=? WHERE userid=?", (currentgamble + amount, context.author.id))
                conn.commit()
                suits = [':hearts:',':spades:',':clubs:',':diamonds:']
                cardvalues = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 'Ace'] #multiple 10s to make up for the j, q, and k
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
                if dealercalc == False:
                    dealertotal = dealer1value + dealer2value
                if player1value == 'Ace' or player2value == 'Ace':
                    playercalc = True
                    if player1value == 10 or player2value == 10:
                        await context.send(f"{context.author.mention} Blackjack. Received {amount*3} cheeseballz back.")
                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal+(amount*2), context.author.id))
                        conn.commit()
                    elif player1value == player2value:
                        playertotal = 12
                    else:
                        if player1value == 'Ace':
                            playertotal = 11 + player2value
                        elif player2value == 'Ace':
                            playertotal = 11 + player1value
                if playercalc == False:
                    playertotal = player1value + player2value
                def msgcheck(m):
                    return m.author == context.author and m.channel == context.channel
                while True:
                    await context.send("Type `hit` or `h` to hit, `stand` or `s` to stand.")
                    response = await client.wait_for('message', check=msgcheck)
                    if response.content.lower() == 'h' or response.content.lower() == 'hit':
                        playernewcardvalue = random.choice(cardvalues)
                        playernewcardsuit = random.choice(suits)
                        if playernewcardvalue == 'Ace':
                            if playertotal + 11 > 21:
                                playertotal = playertotal + 1
                                await context.send(f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}. It has been set to 1.")
                            else:
                                playertotal = playertotal + 11
                                await context.send(f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}. It has been set to 11.")
                        else:
                            playertotal = playertotal + playernewcardvalue
                            await context.send(f"{context.author.mention} You drew a {playernewcardvalue} of {playernewcardsuit}.")
                        if playertotal == 21:
                            await context.send(f"{context.author.mention} You have a total of 21, standing.")
                            break
                        elif playertotal > 21:
                            await context.send(f"{context.author.mention} Bust. Dealer wins.")
                            c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=553840844361170944")
                            bankbal = int(re.sub("[(),'\[\]]", "", str(c.fetchall())))
                            c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=553840844361170944", (bankbal + amount,))
                            conn.commit()
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
                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal+amount, context.author.id))
                    elif dealertotal == playertotal:
                        await context.send(f"{context.author.mention} Push. Received {amount}.")
                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal, context.author.id))
                    elif dealertotal > playertotal:
                        await context.send(f"{context.author.mention} Dealer wins.")
                    else:
                        await context.send(f"{context.author.mention} You won. Received {amount*2}.")
                        c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (bal+amount, context.author.id))
                    conn.commit()

        @client.command(name='gamblelimit',
                        aliases=['setgamblelimit'])
        async def gamblelimit(context, amount:int=None):
            if amount == None:
                await context.send(f"{context.author.mention} Command usage: `!gamblelimit <amount>`")
            else:
                c.execute("UPDATE cheeseballztable SET gamblelimit=? WHERE userid=?", (amount, context.author.id))
                await context.message.add_reaction(check)


def setup(client):
    client.add_cog(Cheeseballz(client))
