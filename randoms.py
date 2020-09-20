#imports
import discord
import random
from discord.ext.commands import Bot
from discord.ext import commands
#class main commands
class Randoms(commands.Cog):
    def __init__(self, client):
        self.client = client

        #rps
        @client.command(name='rps',
                        aliases=['rockpaperscissors'])
        async def rps(context,*, content:str=None):
            rpsChoices = ['Rock', 'Paper', 'Scissors']
            results = ['You won.', 'You lost.', 'We tied.']
            botchoice = random.choice(rpsChoices)
            await context.send(f"I chose `{botchoice}`. You chose `{content}`.")
            if 'Rock' in botchoice:
                if "paper" in selection:
                    await context.send(results[0])
                elif "rock" in selection:
                    await context.send(results[2])
                elif "scissors" in selection:
                    await context.send(results[1])
                else:
                    await context.send(random.choice(results))
            elif 'Paper' in botchoice:
                if "scissors" in selection:
                    await context.send(results[0])
                elif "paper" in selection:
                    await context.send(results[2])
                elif "rock" in selection:
                    await context.send(results[1])
                else:
                    await context.send(random.choice(results))
            elif 'Scissors' in botchoice:
                if "rock" in selection:
                    await context.send(results[0])
                elif "scissors" in selection:
                    await context.send(results[2])
                elif "paper" in selection:
                    await context.send(results[1])
                else:
                    await context.send(random.choice(results))

        #coin flipping
        @client.command(name='coin',
                        aliases=['flipcoin','coinflip','flip'])
        async def coin(context):
            await context.send(random.choice(['Heads.','Tails.']))

        #8ball
        @client.command(name='ball',
                        aliases=['8ball'])
        async def ball(context):
            possible_responses = [
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt.',
            'Yes - definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            "Don't count on it.",
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.',
            ]
            await context.send(random.choice(possible_responses))
#setup/add
def setup(client):
    client.add_cog(Randoms(client))
