import discord
import asyncio
import csv
import re

client = discord.Client()
authUsers = []
authUserFile = "authUsers.csv"
token = 'MzM5NjI0Mjg0NjgxMTQyMjc0.DFmw9g.4s0a1KbjZcY8Y0Ju1TMMEZ2SpWU'



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



@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('Loading AuthUsers...')
    with open(authUserFile, "r", newline = '') as authFile:
        reader = csv.reader(authFile, delimiter = ';', quotechar = '\'')
        for row in reader:
            for item in row:
                if not item == '':
                    authUsers.append(str(item))
    print(str(authUsers))

@client.event
async def on_message(message):
    if message.content.startswith(client.user.mention):
        namesize = len(client.user.mention)
        if message.author.id in authUsers:
            words = re.findall(r"[\w']+", message.content[namesize:])
            if len(words) > 0 and words[0] in commandsList.keys():
                tmp = await commandsList[words[0]](message)
            elif len(message.content) == len(client.user.mention):
                tmp = await client.send_message(message.channel, "Hello, " + message.author.mention + "!")
            else:
                tmp = await client.send_message(message.channel, "I'm sorry, " + message.author.mention + ", I can't do that.")
        else:
            reply = message.author.mention + ", you are not authorized to control this bot."
            tmp = await client.send_message(message.channel, reply)

client.run(token)
