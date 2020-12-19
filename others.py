import discord
from discord.ext import commands


class Others(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='group', aliases=['donate', 'game'])
    async def group(self, context):
        embed = discord.Embed(title="Group and donation links", color=0x00ff00)
        embed.add_field(name="Group", value="https://www.roblox.com/groups/4975741")
        embed.add_field(name="Game", value="https://www.roblox.com/games/5220440891")
        embed.add_field(name="Donation shirts", value="https://www.roblox.com/groups/4975741/TR-Community-Relations#!/store")
        embed.add_field(name="Alternatively:", value="""BTC: 15gfLTLHLkZ2BebpJUhzV38uTTrG2exc8F
ETH: 0x4A58f1bb5305f381FD83416A8E72a63d64FB5c6a""", inline=False)
        embed.set_footer(text="If you donate, DM an Advisory Board+ with proof so you can receive your role(s).")
        await context.send(embed=embed)

    @commands.command(name='purge')
    @commands.check_any(commands.has_guild_permissions(administrator=True), commands.has_role(658897468746104833))
    async def purge(self, context, number: int = None):
        if number is None:
            await context.send(f"{context.author.mention} Command usage: `!purge <number>`")
        elif number > 99:
            await context.send(f"{context.author.mention} {self.client.x} Too many messages. Maximum is 99.")
        else:
            await context.message.add_reaction('\U0001F504')
            messages = []
            async for message in context.channel.history(limit=(number + 1)):
                messages.append(message)
            await context.channel.delete_messages(messages)


def setup(client):
    client.add_cog(Others(client))
