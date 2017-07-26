import discord
import asyncio
import csv
import re
import os

async def test(message):
    tmp = await client.send_message(message.channel, "Testing, 1, 2, 3!")
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
            tmp = await client.send_message(message.channel, "There was no user to deauthorize!")

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
    await client.send_message(message.channel, "Valid commands for this bot: " + str(commandsList.keys()))
    return

commandsList = {
    "test": test,
    "sleep": sleep,
    "authorize": addAuthUser,
    "auth": addAuthUser,
    "op": addAuthUser,
    "deauth": removeAuthUser,
    "deauthorize": removeAuthUser,
    "deop": removeAuthUser,
    "help": dispHelp,
    }

def directory():
    return os.path.dirname(os.path.realpath(__file__))
