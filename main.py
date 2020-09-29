import discord
import time
import sys
import funcs
from discord.ext.commands import Bot

TOKEN = "NTUzODQwODQ0MzYxMTcwOTQ0.XvM3KQ.bE9hZLNejGzehBRvt541TZuwJFk"
# if adding new module, remember to add in updates.py
startup_extensions = ["cheeseballz", "cbgames", "randoms", "presence", "staff", "others", "updates", "exec", "assign",
                      "errorhandler", "jishaku"]
client = Bot(command_prefix='!')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    client.x = client.get_emoji(689001238141861934)
    client.check = client.get_emoji(688998780900737096)
    client.logs = client.get_channel(657112105467772929)
    client.crdguild = client.get_guild(528679766270935040)
    client.cbperms = client.crdguild.get_role(658829550850932736)
    client.requests = client.get_channel(660213957448957952)
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
            print(f"Extension {extension} loaded")
        except Exception as e:
            print(e)


@client.command(name='shutdown')
async def shutdown(context):
    if context.author.id == 291661685863874560:
        await context.message.add_reaction(client.check)
        sys.exit()
    else:
        await funcs.noperms(context, client)


@client.command(name='ping')
async def ping(context):
    beforeping = time.monotonic()
    messageping = await context.send("Pong!")
    pingtime = (time.monotonic() - beforeping) * 1000
    await messageping.edit(content=f"Pong! `{int(pingtime)}ms`")


@client.command(name='load')
async def load(context, extension):
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


@client.command(name='unload')
async def unload(context, extension):
    if context.author.id == 291661685863874560:
        client.unload_extension(extension)
        await context.message.add_reaction(client.check)


@client.command(name='reload')
async def reload(context, extension):
    if context.author.id == 291661685863874560:
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
