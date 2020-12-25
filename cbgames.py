import asyncio
import discord
import random
import sqlite3
from discord.ext import commands
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
    @commands.cooldown(rate=1, per=1, type=BucketType.member)
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
            if random.choice([True, False]):
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
                            c.execute(f"SELECT {playernum} FROM russianroulette WHERE gameid=?", (gameid,))
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
                                c.execute("DELETE FROM russianroulette WHERE gameid=?", (gameid,))
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
    @commands.cooldown(rate=1, per=1, type=BucketType.member)
    async def blackjack(self, context, amount: int = None):
        bal = funcs.getbal(context.author.id)
        if amount is None:
            await context.send(f"{context.author.mention} Command usage: `!blackjack <amount>`")
        elif amount < 50:
            await context.send(f"{context.author.mention} You must bet at least 50 cheeseballz.")
        elif bal < amount:
            await funcs.insufficientcb(context, self.client)
        else:
            # Take money
            funcs.removecb(context.author.id, amount)
            # Generate a list of card values
            dealercards = []
            playercards = []
            cards = {"Ace of :spades:": 11, "2 of ::spades::": 2, "3 of :spades:": 3, "4 of :spades:": 4, "5 of :spades:": 5, "6 of :spades:": 6, "7 of :spades:": 7,
                     "8 of :spades:": 8, "9 of :spades:": 9, "10 of :spades:": 10, "Jack of :spades:": 10, "Queen of :spades:": 10, "King of :spades:": 10,

                     "Ace of :clubs:": 11, "2 of :clubs:": 2, "3 of :clubs:": 3, "4 of :clubs:": 4, "5 of :clubs:": 5, "6 of :clubs:": 6, "7 of :clubs:": 7,
                     "8 of :clubs:": 8, "9 of :clubs:": 9, "10 of :clubs:": 10, "Jack of :clubs:": 10, "Queen of :clubs:": 10, "King of :clubs:": 10,

                     "Ace of :hearts:": 11, "2 of :hearts:": 2, "3 of :hearts:": 3, "4 of :hearts:": 4, "5 of :hearts:": 5, "6 of :hearts:": 6, "7 of :hearts:": 7,
                     "8 of :hearts:": 8, "9 of :hearts:": 9, "10 of :hearts:": 10, "Jack of :hearts:": 10, "Queen of :hearts:": 10, "King of :hearts:": 10,

                     "Ace of :diamonds:": 11, "2 of :diamonds:": 2, "3 of :diamonds:": 3, "4 of :diamonds:": 4, "5 of :diamonds:": 5, "6 of :diamonds:": 6, "7 of :diamonds:": 7,
                     "8 of :diamonds:": 8, "9 of :diamonds:": 9, "10 of :diamonds:": 10, "Jack of :diamonds:": 10, "Queen of :diamonds:": 10, "King of :diamonds:": 10}

            for i in range(2):
                playercards.append(random.choice(list(cards)))
                dealercards.append(random.choice(list(cards)))

            await context.send(f"""{context.author.mention} Your cards are:
- **{playercards[0]}**
- **{playercards[1]}**

The dealer's cards are:
- Hidden Card
- **{dealercards[1]}**
""")

            def check(m):
                return m.author == context.author and m.channel == context.channel

            def gettotal(cardset):
                total = 0
                for card in cardset:
                    total = total + cards[card]
                if total > 21:
                    for card in cardset:
                        if "Ace" in card:
                            total = total - 10
                            if total <= 21:
                                break
                return total

            status = "ongoing"

            # Check if player has a blackjack
            if gettotal(playercards) == 21:
                await context.send(f"{context.author.mention} Blackjack. Received {amount*3} cb back.")
                funcs.addcb(context.author.id, amount*3)
                status = "ended"

            # Player actions
            while status == "ongoing":
                await context.send("What would you like to do? [hit/stand/double down]")
                turn = await self.client.wait_for('message', check=check)
                if turn.content.lower() == 'hit':
                    newcard = random.choice(list(cards))
                    await context.send(f"{context.author.mention} You drew a **{newcard}**.")
                    playercards.append(newcard)
                    if gettotal(playercards) > 21:
                        await context.send(f"{context.author.mention} Bust. You have a total of {gettotal(playercards)}.")
                        status = "player_bust"
                elif turn.content.lower() == 'stand':
                    await context.send(f"{context.author.mention} Standing with a total of {gettotal(playercards)}.")
                    break
                elif turn.content.lower() == 'doubledown' or turn.content.lower() == 'double down':
                    # Remove CB again
                    funcs.removecb(context.author.id, amount)
                    amount = amount * 2
                    # Give another card and end
                    newcard = random.choice(list(cards))
                    await context.send(f"{context.author.mention} Your final card is a **{newcard}**.")
                    playercards.append(newcard)
                    if gettotal(playercards) > 21:
                        await context.send(f"{context.author.mention} Bust. You have a total of {gettotal(playercards)}.")
                        status = "player_bust"
                    break
                else:
                    await context.send(f"{context.author.mention} Unrecognized selection.")

            # Dealer actions - continue hitting until total is more than 16
            while gettotal(dealercards) <= 16 and status != "player_bust" and status != "ended":
                await asyncio.sleep(0.5)
                newcard = random.choice(list(cards))
                await context.send(f"Dealer draws a **{newcard}**.")
                dealercards.append(newcard)
                if gettotal(dealercards) > 21:
                    await context.send(f"{context.author.mention} Dealer busted with a total of {gettotal(dealercards)}.")
                    status = "dealer_bust"
                    break

            if status == "ongoing":
                # ONGOING is when player doesn't bust and dealer doesn't bust
                # Display all player cards
                cardmsg = " "
                for card in playercards:
                    cardmsg = cardmsg + f"\n- **{card}**"
                cardmsg = cardmsg + "\n\nThe dealer's cards are:"
                for card in dealercards:
                    cardmsg = cardmsg + f"\n- **{card}**"
                await context.send(f"{context.author.mention} Your cards are:{cardmsg}")

                await asyncio.sleep(1)

                # Result calculations
                await context.send(f"{context.author.mention} You have a total of {gettotal(playercards)}. The dealer has a total of {gettotal(dealercards)}.")

                # Notify user of winner
                if gettotal(dealercards) > gettotal(playercards):
                    await context.send(f"{context.author.mention} Dealer wins.")
                elif gettotal(playercards) > gettotal(dealercards):
                    await context.send(f"{context.author.mention} You win. Received {amount*2} cb back.")
                    funcs.addcb(context.author.id, amount*2)
                elif gettotal(playercards) == gettotal(dealercards):
                    await context.send(f"{context.author.mention} Push. Received {amount} cb back.")
                    funcs.addcb(context.author.id, amount)

            elif status == "player_bust":
                # PLAYER_BUST when player has gone over 21
                await context.send(f"{context.author.mention} Dealer wins.")
            elif status == "dealer_bust":
                # DEALER_BUST when dealer has gone over 21
                await context.send(f"{context.author.mention} You win. Received {amount*2} cb back.")
                funcs.addcb(context.author.id, amount*2)


def setup(client):
    client.add_cog(CBgames(client))
