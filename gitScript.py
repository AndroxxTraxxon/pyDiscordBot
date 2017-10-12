import discord
# import asyncio
import csv
# import re
import os

global client
global authUserFile
global authUsers
global muted


def initSequence(my_client, my_AUF, my_AU):
    global client
    client = discord.Client(my_client)
    global authUserFile
    authUserFile = str(my_AUF)
    global authUsers
    authUsers = list(my_AU)
    return


async def mute(message):
    global muted
    muted = True
    tmp = await client.send_message(message.channel, "... hmph ...")
    return tmp


async def unmute(message):
    global muted
    muted = False
    tmp = await client.send_message(message.channel, "Ahhh, Freedom!")
    return tmp


async def test(message):
    tmp = await client.send_message(message.channel, "Testing, 1, 2, 3!")
    return tmp


async def sleep(message):
    tmp = await client.send_message(message.channel, "Goodnight!")
    await client.close()
    return tmp


async def addAuthUser(message):
    mentionList = []
    with open(authUserFile, 'w', newline='') as authFile:
        for mention in message.mentions:
            if (not mention.id == client.user.id) and\
                    (mention.id not in authUsers):
                writer = csv.writer(authFile, delimiter=';',
                                    quotechar='\'',
                                    quoting=csv.QUOTE_MINIMAL)
                authUsers.append(mention.id)
                writer.writerow(authUsers)
                mentionList.append(mention.mention)

        if len(mentionList) > 0:
            tmp = await client.send_message(message.channel,
                                            "Authorizing " + str(mentionList))
            print("AuthUsers Updated:")
            print(str(authUsers))
        else:
            tmp = await client.send_message(message.channel,
                                            "There was no user to authorize!")
            return tmp


async def removeAuthUser(message):
    mentionList = []
    with open(authUserFile, 'w', newline='') as authFile:
        for mention in message.mentions:
            if not mention.id == client.user.id and mention.id in authUsers:
                writer = csv.writer(authFile, delimiter=';',
                                    quotechar='\'', quoting=csv.QUOTE_MINIMAL)
                authUsers.remove(mention.id)
                writer.writerow(authUsers)
                mentionList.append(mention.mention)

        if len(mentionList) > 0:
            tmp = await client.send_message(message.channel, "Deauthorizing "
                                            + str(mentionList))
            print("AuthUsers Updated:")
            print(str(authUsers))
        else:
            tmp = await client.send_message(message.channel,
                                            "There was no user to authorize!")
            return tmp


async def dispHelp(message):
    tmp = await client.send_message(message.channel,
                                    "Valid commands for this bot: "
                                    + str(commandsList.keys()))
    return tmp


async def dispAdminHelp(message):
    tmp = await client.send_message(message.author,
                                    "Valid admin commands for this bot: "
                                    + str(commandsListAdmin.keys())
                                    + "\n or \"sudo update\" to refresh"
                                    + " the bot command set.")
    return tmp

commandsListAdmin = {
    "sleep": sleep,
    "authorize": addAuthUser,
    "auth": addAuthUser,
    "op": addAuthUser,
    "deauth": removeAuthUser,
    "deauthorize": removeAuthUser,
    "deop": removeAuthUser,
    "help": dispAdminHelp,
}

commandsList = {
    "help": dispHelp,
    "test": test
}


def directory():
    return os.path.dirname(os.path.realpath(__file__))
