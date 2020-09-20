#imports
import discord
import time
import sys
import random
from discord.ext.commands import Bot
from datetime import datetime
from discord.ext.commands import CommandNotFound
from discord.ext import commands
#starting things
TOKEN = "NTUzODQwODQ0MzYxMTcwOTQ0.XvM3KQ.bE9hZLNejGzehBRvt541TZuwJFk"
#LOAD EXTENSIONS HERE
# if adding new module, remember to add in updates.py
startup_extensions = ["cheeseballz", "randoms", "presence", "staff", "others", "updates", "exec", "assign", "errorhandler", "jishaku"]
client = Bot(command_prefix='!')
#starting events
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
            print(f"Extension {extension} loaded")
        except Exception as e:
            print(e)
#shutdown command
@client.command(name='shutdown')
async def shutdown(context):
    x = client.get_emoji(689001238141861934)
    check = client.get_emoji(688998780900737096)
    head = context.guild.get_role(528682495089180682)
    overseer = context.guild.get_role(528682488613306379)
    if head in context.author.roles or overseer in context.author.roles or context.author.id == 291661685863874560:
        await context.message.add_reaction(check)
        print(f"{context.author} shutdown at {time.ctime()}")
        sys.exit()
    else:
        await context.send(f"{context.author.mention} {x} Insufficient permissions.")
#ping
@client.command(name='ping')
async def ping(context):
    beforeping = time.monotonic()
    messageping = await context.send("Pong!")
    pingtime = (time.monotonic() - beforeping) * 1000
    await messageping.edit(content = f"Pong! `{int(pingtime)}ms`")
#load extension manually
@client.command(name='load')
async def load(context,extension:str):
    check = client.get_emoji(688998780900737096)
    if context.author.id == 291661685863874560:
        try:
            client.load_extension(extension)
            await context.message.add_reaction(check)
        except Exception as e:
            try:
                await context.send(e)
            except discord.errors.HTTPException as e:
                print(e)
                await context.send("Error exceeds Discord character limit. See console for details.")
#unload extension manually
@client.command(name='unload')
async def unload(context,extension:str):
    check = client.get_emoji(688998780900737096)
    if context.author.id == 291661685863874560:
        client.unload_extension(extension)
        await context.message.add_reaction(check)
#reload extensions
@client.command(name='reload')
async def reload(context, extension:str):
    check = client.get_emoji(688998780900737096)
    if context.author.id == 291661685863874560:
        try:
            client.unload_extension(extension)
            client.load_extension(extension)
            await context.message.add_reaction(check)
        except Exception as e:
            try:
                await context.send(e)
            except discord.errors.HTTPException as e:
                print(e)
                await context.send("Error exceeds Discord character limit. See console for details.")
#run
client.run(TOKEN)
