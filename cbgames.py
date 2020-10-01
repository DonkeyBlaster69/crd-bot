import asyncio
import discord
from discord.ext import commands
import random
import sqlite3
from discord.ext.commands import BucketType
import funcs

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()


class CBgames(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name='slots')
    @commands.cooldown(rate=1, per=4, type=BucketType.member)
    async def slots(self, context, amount: int = None):
        bal = funcs.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!slots <amount>`")
        elif amount < 50:
            await context.send(f"{context.author.mention} You must bet a minimum of 50 cheeseballz. You currently have {bal} cheeseballz.")
        elif bal < amount:
            await funcs.insufficientcb(context, self.client)
        else:
            funcs.addgamble(context.author.id, amount)
            funcs.removecb(context.author.id, amount)

            # Define list with one element, to line up rolls and indexes
            roll = ['placeholder']
            # Append random emojis to the list 18 times
            for i in range(18):
                roll.append(random.choice([':strawberry:', ':pear:', ':tangerine:', ':grapes:', ':watermelon:']))

            # Continously edit messages to have a slots animation
            rollmsg = await context.send(f"""{context.author.mention} Slots:
            :heavy_minus_sign:{roll[1]} | {roll[2]} | {roll[3]}:heavy_minus_sign:
            :arrow_forward:{roll[4]} | {roll[5]} | {roll[6]}:arrow_backward:
            :heavy_minus_sign:{roll[7]} | {roll[8]} | {roll[9]}:heavy_minus_sign:""")
            await asyncio.sleep(1)
            await rollmsg.edit(content=f"""{context.author.mention} Slots:
            :heavy_minus_sign:{roll[4]} | {roll[5]} | {roll[6]}:heavy_minus_sign:
            :arrow_forward:{roll[7]} | {roll[8]} | {roll[9]}:arrow_backward:
            :heavy_minus_sign:{roll[10]} | {roll[11]} | {roll[12]}:heavy_minus_sign:""")
            await asyncio.sleep(1)
            await rollmsg.edit(content=f"""{context.author.mention} Slots:
            :heavy_minus_sign:{roll[7]} | {roll[8]} | {roll[9]}:heavy_minus_sign:
            :arrow_forward:{roll[10]} | {roll[11]} | {roll[12]}:arrow_backward:
            :heavy_minus_sign:{roll[13]} | {roll[14]} | {roll[15]}:heavy_minus_sign:""")
            await asyncio.sleep(1)
            await rollmsg.edit(content=f"""{context.author.mention} Slots:
            :heavy_minus_sign:{roll[10]} | {roll[11]} | {roll[12]}:heavy_minus_sign:
            :arrow_forward:{roll[13]} | {roll[14]} | {roll[15]}:arrow_backward:
            :heavy_minus_sign:{roll[16]} | {roll[17]} | {roll[18]}:heavy_minus_sign:""")

            # If the second last lines are all the same, give the winning amount
            if roll[13] == roll[14] and roll[14] == roll[15]:
                await context.send(f"{context.author.mention} Congrats! Received {amount * 12} cheeseballz back.")
                winnings = amount * 12
                funcs.addcb(context.author.id, winnings)
            else:
                await context.send(f"{context.author.mention} Sorry, try again.")

    @commands.command(name='double', aliases=['dub', 'doub'])
    @commands.cooldown(rate=1, per=2, type=BucketType.member)
    async def double(self, context, amount: int = None):
        bal = funcs.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!double <amount>`")
        elif amount < 10:
            await context.send(f"{context.author.mention} You must be at least 10 cheeseballz.")
        elif bal < amount:
            await funcs.insufficientcb(context, self.client)
        else:
            funcs.addgamble(context.author.id, amount)
            funcs.removecb(context.author.id, amount)
            if random.choice([True, False]) is True:
                await context.send(f"{context.author.mention} Congrats! Received {amount*2} cheeseballz back.")
                funcs.addcb(context.author.id, amount * 2)
            else:
                await context.send(f"{context.author.mention} Sorry, try again.")

    @commands.command(name='russianroulette', aliases=['rr'])
    async def russianroulette(self, context, operation: str = None, gameid: int = None, amount: int = None):
        bal = funcs.getbal(context.author.id)
        if operation is None or gameid is None:
            await context.send(f"{context.author.mention} Command usage: `!rr <new/join> <gameid> <amount>`")
        else:
            if operation == 'new':
                if bal < amount:
                    await funcs.insufficientcb(context, self.client)
                else:
                    funcs.removecb(context.author.id, amount)
                    funcs.addgamble(context.author.id, amount)
                    c.execute("INSERT INTO russianroulette(gameid, amount, player1, started) VALUES (?, ?, ?, 0)", (gameid, amount, context.author.id))
                    conn.commit()
                    embed = discord.Embed(title="Russian Roulette", color=0xffa500)
                    embed.add_field(name="Game ID", value=str(gameid), inline=True)
                    embed.add_field(name="Bet Amount", value=str(amount), inline=True)
                    embed.add_field(name="Player 1", value=context.author.mention, inline=False)
                    await context.send(embed=embed)
                    await asyncio.sleep(20)
                    # All the code above should have created a new game and inserted it into the SQL DB
                    # The code below should run after 20 seconds has passed from creating the new game
                    # That should give enough time for people in that channel to join the game if they want

                    # First bit here checks if there are actually other players in the game
                    # If not, it deletes the game and refunds the original CB taken
                    c.execute("SELECT player2 FROM russianroulette WHERE gameid=?", (gameid,))
                    if str(c.fetchone()[0]) == "None":
                        await context.send(f"{context.author.mention} Not enough players joined to start the game. Cancelling and refunding CB.")
                        c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                        conn.commit()
                        funcs.addcb(context.author.id, amount)
                    else:
                        c.execute("UPDATE russianroulette SET started=1 WHERE gameid=?", (gameid,))
                        conn.commit()
                        await context.send(f"Starting game {gameid}.")
                        players = []

                        # Goes through all the players for that game in the SQL DB
                        # Players are appended to list "players"
                        # Players are counted and stored to "originalPlayers"
                        for i in range(1, 7):
                            playernum = 'player' + str(i)
                            c.execute("SELECT ? FROM russianroulette WHERE gameid=?", (playernum, gameid))
                            player = str(c.fetchone()[0])
                            if player != 'None':
                                players.append(player)
                        originalPlayers = len(players)

                        # Refresh chamber function resets the "bullets" for the list of players
                        # This uses len(players) instead of originalPlayers because we need to reset when players die
                        # Returns list of 0's and 1's for bullets
                        def refreshchamber():
                            chamberfunction = []
                            for i in range(len(players)):
                                chamberfunction.append(random.randint(0, 1))
                            return chamberfunction
                        chamber = refreshchamber()

                        # This function takes "fireindex" and uses that to sync up the "players" list and the "chamber" list
                        # If the "chamber" list returns a 0, that player survives
                        # If the "chamber" list returns a 1, that player is shot and the function returns the player number that was shot
                        async def fire(fireindex):
                            await asyncio.sleep(2)
                            if chamber[fireindex] == 0:
                                await context.send(f"<@{players[fireindex]}> pulls the trigger and... survives!")
                            else:
                                await context.send(f"<@{players[fireindex]}> pulls the trigger and... gets shot!")
                                return fireindex

                        # First for loop goes through all the remaining players and determines if they should be removed or not
                        toRemove = []
                        while True:
                            chamber = refreshchamber()
                            for i in range(len(players)):
                                pending = await fire(i)
                                if pending is not None:
                                    toRemove.append(pending)

                            # Checks if the toRemove list is empty. If not, remove the players in it and clear it
                            if toRemove != []:
                                toRemove.reverse()
                                for i in toRemove:
                                    players.pop(i)
                                toRemove = []

                            # Checks if there are one or zero players left in game
                            if len(players) == 0:
                                await context.send(f"No one won game {gameid}.")
                                c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
                                conn.commit()
                                break
                            elif len(players) == 1:
                                winner = int(players[0])
                                await context.send(f"<@{winner}> has won the game!")
                                toAdd = amount * originalPlayers
                                funcs.addcb(winner, toAdd)
                                await context.send(f"{toAdd} cheeseballz has been deposited to <@{winner}>'s account.")
                                c.execute("DELETE FROM russianroulette WHERE gameid=", (gameid,))
                                conn.commit()
                                break
            elif operation == 'join':
                c.execute("SELECT started FROM russianroulette WHERE gameid=?", (gameid,))
                started = str(c.fetchone()[0])
                # If clause checks if game has started, else checks if they have the cb. If they do, keep going
                if started == '1' or started == 'None':
                    await context.send(f"{context.author.mention} The specified game does not exist or has already started.")
                else:
                    c.execute("SELECT amount FROM russianroulette WHERE gameid=?", (gameid,))
                    amount = int(c.fetchone()[0])
                    if bal < amount:
                        await funcs.insufficientcb(context, self.client)
                    else:
                        # Function that takes in "playernum" in the format of "player2" and so on, and attempts to parse the game
                        # After parsing, it adds a player if the game has an empty space
                        def attemptjoin(playernum):
                            c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?", (gameid,))
                            if c.fetchone()[0] is None:
                                c.execute(f"UPDATE russianroulette SET {playernum}=? WHERE gameid=?", (context.author.id, gameid))
                                conn.commit()
                                funcs.removecb(context.author.id, amount)
                                return True
                            else:
                                return False

                        # This loop iterates through the possible empty spots in a game and just checks if the player has joined or not with the return
                        for i in range(2, 7):
                            playernum = ('player' + str(i))
                            if attemptjoin(playernum) is True:
                                await context.send(f"{context.author.mention} Joined game {gameid} as player {i}, betting {amount} cheeseballz.")
                                break

    @commands.command(name='blackjack', aliases=['bj'])
    @commands.cooldown(rate=1, per=30, type=BucketType.member)
    async def blackjack(self, context, amount: int = None):
        bal = funcs.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!blackjack <amount>`")
        elif amount < 50:
            await context.send(f"{context.author.mention} You must be at least 50 cheeseballz.")
        elif bal < amount:
            await funcs.insufficientcb(context, self.client)
        else:
            # Generate a list of card values
            cards = {"Ace of Spades": 1, "Two of Spades": 2, "Three of Spades": 3, "Four of Spades": 4, "Five of Spades": 5, "Six of Spades": 6, "Seven of Spades": 7,
                     "Eight of Spades": 8, "Nine of Spades": 9, "Ten of Spades": 10, "Jack of Spades": 10, "Queen of Spades": 10, "King of Spades": 10,

                     "Ace of Clubs": 1, "Two of Clubs": 2, "Three of Clubs": 3, "Four of Clubs": 5, "Five of Clubs": 5, "Six of Clubs": 6, "Seven of Clubs": 7,
                     "Eight of Clubs": 8, "Nine of Clubs": 9, "Ten of Clubs": 10, "Jack of Clubs": 10, "Queen of Clubs": 10, "King of Clubs": 10,

                     "Ace of Hearts": 1, "Two of Hearts": 2, "Three of Hearts": 3, "Four of Hearts": 5, "Five of Hearts": 5, "Six of Hearts": 6, "Seven of Hearts": 7,
                     "Eight of Hearts": 8, "Nine of Hearts": 9, "Ten of Hearts": 10, "Jack of Hearts": 10, "Queen of Hearts": 10, "King of Hearts": 10,

                     "Ace of Diamonds": 1, "Two of Diamonds": 2, "Three of Diamonds": 3, "Four of Diamonds": 5, "Five of Diamonds": 5, "Six of Diamonds": 6, "Seven of Diamonds": 7,
                     "Eight of Diamonds": 8, "Nine of Diamonds": 9, "Ten of Diamonds": 10, "Jack of Diamonds": 10, "Queen of Diamonds": 10, "King of Diamonds": 10}


def setup(client):
    client.add_cog(CBgames(client))
