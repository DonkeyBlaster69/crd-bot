from discord.ext import commands


class MemberCount(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def updatemembers(self, guild):
        # Goes through all the members in the server and checks if they're a bot
        bots = []
        for member in guild.members:
            if member.bot is True:
                bots.append(member)
        # Edits channel names to update them, clientvars are under main.py after on_ready
        await self.client.membercount_channel.edit(name=f"Member Count: {guild.member_count}")
        await self.client.botcount_channel.edit(name=f"Bot Count: {len(bots)}")
        await self.client.usercount_channel.edit(name=f"User Count: {guild.member_count - len(bots)}")

    @commands.command(name="countmembers", aliases=['updatecounters', 'membercount'])
    async def countmembers(self, context):
        await self.updatemembers(guild=context.guild)
        await context.message.add_reaction(self.client.check)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.updatemembers(guild=member.guild)


def setup(client):
    client.add_cog(MemberCount(client))
