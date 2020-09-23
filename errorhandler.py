from discord.ext import commands


class ErrorHandler(commands.Cog):

    @commands.Cog.listener
    async def on_command_error(self, context, exception):

        error = getattr(exception, 'original', exception)

        if isinstance(error, commands.CommandOnCooldown):
            await context.send(error)
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            raise error


def setup(client):
    client.add_cog(ErrorHandler(client))
