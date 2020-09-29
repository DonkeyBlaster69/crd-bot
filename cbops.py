import sqlite3
from main import client

conn = sqlite3.connect('cheeseballz.db')
c = conn.cursor()


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


async def insufficientcb(context):
    await context.send(f"{context.author.mention} {client.x} Not enough cheeseballz. You currently have {getbal(context.author.id)} cheeseballz.")