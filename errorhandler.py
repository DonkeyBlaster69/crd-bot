from discord.ext import commands
import funcs


class ErrorHandler(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, context, exception):
        error = getattr(exception, 'original', exception)

        if isinstance(error, commands.CommandOnCooldown):
            await context.send(error)
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, (commands.NotOwner or commands.MissingPermissions or commands.MissingRole)):
            await funcs.noperms(context, self.client)
        else:
            raise error


def setup(client):
    client.add_cog(ErrorHandler(client))
