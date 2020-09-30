import os
import funcs
from discord.ext import commands


class Updates(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='update', aliases=['pushupdates', 'push'])
    @commands.is_owner()
    async def update(self, context):
        repo_url = "https://github.com/DonkeyBlaster69/crd-bot.git"
        await context.send(f"Cloning from `{repo_url}`.")
        cloneexit = os.system(f"git clone {repo_url} ~/crd-bot-temp")
        if cloneexit == 0:
            await context.send("Cloned to crd-bot-temp. Copying .py files.")
            copyexit = os.system("cd ~/crd-bot-temp && cp ~/crd-bot-temp/*.py ~/crd-bot")
            if copyexit == 0:
                await context.send("Finished copying files. Reloading modules and deleting temporary clone folder.")
                os.system("sudo rm ~/crd-bot-temp -r")
                for extension in funcs.startup_extensions:
                    try:
                        self.client.load_extension(extension)
                    except Exception as e:
                        context.send(e)
                await context.message.add_reaction(self.client.check)


def setup(client):
    client.add_cog(Updates(client))
