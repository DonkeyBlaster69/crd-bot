import sqlite3

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()

startup_extensions = ["cheeseballz", "cbgames", "randoms", "presence", "staff", "others", "updates", "exec", "assign",
                      "membercount", "errorhandler", "jishaku"]


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
    c.execute("UPDATE cheeseballztable SET totalgamble=? WHERE userid=?", (int(c.fetchone()[0]) + amount, userid))
    conn.commit()


async def insufficientcb(context, client):
    await context.send(f"{context.author.mention} {client.x} Not enough cheeseballz. You currently have {getbal(context.author.id)} cheeseballz.")


async def noperms(context, client):
    await context.send(f"{context.author.mention} {client.x} Insufficient permissions.")
