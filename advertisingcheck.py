import asyncio
from datetime import datetime, timedelta
from discord.ext import commands


class AdvertisingCheck(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        # If channel is the advert channel, and if author joined within the last 48h
        # Delete the advert message and notify the author
        if message.channel.id == 663241106372427790:
            if message.author.joined_at + timedelta(hours=48) > datetime.now():
                waitmsg = await message.channel.send(f"{message.author.mention} {self.client.x} Please wait 48 hours before advertising in this channel. Your message has been DM'ed to you.")
                await message.author.send(f"Your original message is here: ```{message.content}```")
                await message.delete()
                await asyncio.sleep(5)
                await waitmsg.delete()


def setup(client):
    client.add_cog(AdvertisingCheck(client))
