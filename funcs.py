import sqlite3

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()

startup_extensions = ["updates", "cheeseballz", "cbgames", "randoms", "presence", "staff", "others", "exec", "assign",
                      "membercount", "errorhandler", "advertisingcheck", "roles", "smite", "jishaku"]


def addcb(userid, amount):
    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
    balance = int(c.fetchone()[0])
    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (balance + amount, userid))
    conn.commit()


def removecb(userid, amount):
    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
    balance = int(c.fetchone()[0])
    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (balance - amount, userid))
    conn.commit()


def setcb(userid, amount):
    c.execute("UPDATE cheeseballztable SET cheeseballz=? WHERE userid=?", (amount, userid))
    conn.commit()


def getbal(userid):
    c.execute("SELECT cheeseballz FROM cheeseballztable WHERE userid=?", (userid,))
    return int(c.fetchone()[0])


def addgamble(userid, amount):
    c.execute("SELECT totalgamble FROM cheeseballztable WHERE userid=?", (userid,))
    newgambled = int(c.fetchone()[0]) + int(amount)
    c.execute("UPDATE cheeseballztable SET totalgamble=? WHERE userid=?", (newgambled, userid))
    conn.commit()


async def insufficientcb(context, client):
    await context.send(f"{context.author.mention} {client.x} Not enough cheeseballz. You currently have {getbal(context.author.id)} cheeseballz.")


async def noperms(context, client):
    await context.send(f"{context.author.mention} {client.x} Insufficient permissions.")
