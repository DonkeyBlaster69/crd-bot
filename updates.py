import discord
import os
from discord.ext import commands


class Updates(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='update', aliases=['pushupdates', 'push'])
    async def update(self, context):
        if context.author.id == 291661685863874560:
            await context.send("Copying files...")
            exitcode = os.system("mv ~/share/updates/* ~")
            # module list ---
            modules = ["updates", "cheeseballz", "randoms", "presence", "staff", "others", "exec", "assign",
                       "membercount", "errorhandler"]
            currentmodule = 0
            # ---------------
            if exitcode == 0:
                modulemsg = await context.send("Reloading modules...")
                while True:
                    if currentmodule == len(modules):
                        await modulemsg.edit(content="Finished pushing updates from `~/share/updates`.")
                    else:
                        try:
                            self.client.unload_extension(modules[currentmodule])
                        except Exception as e:
                            await context.send(f"`{e}` Moving on.")
                        try:
                            self.client.load_extension(modules[currentmodule])
                            currentmodule = currentmodule + 1
                        except Exception as e:
                            await context.send(f"Failed loading {modules[currentmodule]}.")
                            try:
                                await context.send(e)
                                break
                            except discord.errors.HTTPException as e:
                                print(e)
                                await context.send("Error exceeds Discord character limit. See console for details.")
                                break
            elif exitcode == 256:
                await context.send("`~/share/updates` is empty or does not exist.")
            else:
                await context.send(f"Error copying files. Exit code `{exitcode}`.")


def setup(client):
    client.add_cog(Updates(client))
