from discord.ext import commands


class Roles(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 779613003661705246:

            guild = await self.client.get_guild(payload.guild_id)
            member = await guild.get_member(payload.member_id)

            qotd = await guild.get_role(656878039430594601)
            competition = await guild.get_role(656875723482595338)
            giveaway = await guild.get_role(656797072938237971)

            if str(payload.emoji) == '📰':  # Newspaper \U0001f4f0
                await member.add_roles(qotd)
                await member.send("You've been given the QOTD Notifications role.")

            elif str(payload.emoji) == '🏆':  # Trophy \U0001f3c6
                await member.add_roles(competition)
                await member.send("You've been given the Competition Notifications role.")

            elif str(payload.emoji) == '💰':  # Moneybag \U0001f4b0
                await member.add_roles(giveaway)
                await member.send("You've been given the Giveaway Notifications role.")



    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):


def setup(client):
    client.add_cog(Roles(client))