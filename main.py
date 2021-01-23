import discord
import time
import sys
import funcs
from discord.ext.commands import Bot
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

TOKEN = open("token.txt", "r").read()
client = Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # Emoji defs
    client.x = client.get_emoji(689001238141861934)
    client.check = client.get_emoji(688998780900737096)
    # CB perms role as well as guild
    client.crdguild = client.get_guild(528679766270935040)
    client.cbperms = client.crdguild.get_role(658829550850932736)
    # CRD Bot logs channel and CB requests channel
    client.logs = client.get_channel(657112105467772929)
    client.requests = client.get_channel(660213957448957952)
    # Member count channel defs
    client.membercount_channel = client.get_channel(544800224883900416)
    client.usercount_channel = client.get_channel(544800225945059338)
    client.botcount_channel = client.get_channel(544800226582593536)
    # Iterate through startup_extensions and attempt to load
    for extension in funcs.startup_extensions:
        try:
            client.load_extension(extension)
            print(f"Extension {extension} loaded")
        except Exception as e:
            print(e)


@client.command(name='shutdown')
@commands.is_owner()
async def shutdown(context):
    await context.message.add_reaction(client.check)
    sys.exit()


@client.command(name='ping')
async def ping(context):
    beforeping = time.monotonic()
    messageping = await context.send("Pong!")
    pingtime = (time.monotonic() - beforeping) * 1000
    await messageping.edit(content=f"Pong! `{int(pingtime)}ms`")


@client.command(name='load')
@commands.is_owner()
async def load(context, extension):
    try:
        client.load_extension(extension)
        await context.message.add_reaction(client.check)
    except Exception as e:
        try:
            await context.send(e)
        except discord.errors.HTTPException as e:
            print(e)
            await context.send("Error exceeds Discord character limit. See console for details.")


@client.command(name='unload')
@commands.is_owner()
async def unload(context, extension):
    client.unload_extension(extension)
    await context.message.add_reaction(client.check)


@client.command(name='reload')
@commands.is_owner()
async def reload(context, extension):
    try:
        client.unload_extension(extension)
        client.load_extension(extension)
        await context.message.add_reaction(client.check)
    except Exception as e:
        try:
            await context.send(e)
        except discord.errors.HTTPException as e:
            print(e)
            await context.send("Error exceeds Discord character limit. See console for details.")


client.run(TOKEN)
