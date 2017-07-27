import discord
import asyncio
import csv
import re
import os

muted = False

foulMouth = [
    "fuck",
    "fucker",
    "fucking",
    "fuker",
    "fuk",
    "fuckin",
    "shit",
    "motherfucker",
    "damn",
    "bastard",
    "dick",
    "bitch",
    "cock"
]

async def send_message(channel, message):
    global muted
    tmp = None
    if not muted:
        tmp = await client.send_message(channel, message)
    return tmp

### DEFINE ADMIN COMMANDS HERE ###

async def test(message):
    tmp = await send_message(message.channel, "Testing, 1, 2, 3!")
    return tmp

async def sleep(message):
    tmp = await client.send_message(message.channel, "Goodnight!")
    tmp2 = await client.close()
    return tmp2

async def addAuthUser(message):
    mentionList = []
    with open(authUserFile, 'w', newline='') as authFile:
        for mention in message.mentions:
            if not mention.id == client.user.id and mention.id not in authUsers:
                writer = csv.writer(authFile, delimiter = ';',
                    quotechar = '\'', quoting = csv.QUOTE_MINIMAL)
                authUsers.append(mention.id)
                writer.writerow(authUsers)
                mentionList.append(mention.mention)

        if len(mentionList) > 0:
            tmp = await client.send_message(message.channel, "Authorizing " + str(mentionList))
            print("AuthUsers Updated:")
            print(str(authUsers))
        else:
            tmp = await client.send_message(message.channel, "There was no user to authorize!")

async def removeAuthUser(message):
    mentionList = []
    with open(authUserFile, 'w', newline='') as authFile:
        for mention in message.mentions:
            if not mention.id == client.user.id and mention.id in authUsers:
                writer = csv.writer(authFile, delimiter = ';',
                    quotechar = '\'', quoting = csv.QUOTE_MINIMAL)
                authUsers.remove(mention.id)
                writer.writerow(authUsers)
                mentionList.append(mention.mention)

        if len(mentionList) > 0:
            tmp = await client.send_message(message.channel, "Deauthorizing " + str(mentionList))
            print("AuthUsers Updated:")
            print(str(authUsers))
        else:
            tmp = await client.send_message(message.channel, "There was no user to authorize!")

async def dispHelp(message):
    await client.send_message(message.channel, "Valid user commands for this bot: " + str(userCommandsList.keys()))
    if message.author.id in authUsers:
        await client.send_message(message.author, "Valid admin commands for this bot: " + str(adminCommandsList.keys()))

async def unmute(message):
    global muted
    muted = False
    tmp = await client.send_message(message.channel, "I can :musical_note:SING:musical_note:  again! :notes:LAAAAA DEE DEE DAAAAAA!:notes: ")

### DEFINE USER COMMANDS HERE ###
async def say(message):
    isAdmin = False
    if message.author.id in authUsers:
        isAdmin = True
    words = re.findall(r"[\w']+", message.content[len(client.user.mention):])
    if words[0] == "sudo":
        words.remove("sudo")
    words.remove("say")
    if words[0] in {"hi", "hello", "hey"} or(len(words) >= 2 and words[0] in {"good"} and words[1] in {"morning", "day", "afternoon", "evening",}):
        reply = "My grandma wants me to say " + words[0]
        if len(words) > 1:
            reply += " " + words[1]
        tmp = await send_message(message.channel, reply)

    elif len(words) >= 2 and words[0] == "good" and words[1] == "night":
        if isAdmin:
            tmp = await sleep(message)
        else:
            tmp = await send_message(message.channel, "You can't make me go to bed!")
    else:
        tmp = await send_message(message.channel, "Why would I say that? It's not that funny...")
    return tmp

async def mute(message):
    global muted
    muted = True
    tmp = await client.send_message(message.channel, "YOU CAN'T CONTROL THE MMM MHM HMH MMMMH!")
    return tmp

userCommandsList = {
    "test": test,
    "say" : say,
    "mute": mute
    }

adminCommandsList = {
    "sleep": sleep,
    "authorize": addAuthUser,
    "auth": addAuthUser,
    "op": addAuthUser,
    "deauth": removeAuthUser,
    "deauthorize": removeAuthUser,
    "deop": removeAuthUser,
    "help": dispHelp,
    "unmute": unmute
    }
for key in userCommandsList.keys():
    adminCommandsList[key] = userCommandsList[key]

def directory():
    return os.path.dirname(os.path.realpath(__file__))
