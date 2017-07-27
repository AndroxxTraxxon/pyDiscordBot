import discord
import asyncio
import csv
import re
import os
import importlib
import git
import gitScript
import botToken # you write this file! copy from botToken.py.sample.

client = discord.Client()
gitScript.client = client
authUsers = []
authUserFile = "authUsers.csv"
gitScript.authUserFile = authUserFile
gitScript.authUsers = authUsers


async def reloadGit(message):
    await client.send_message(message.channel, "Updating Command Set...")
    my_repo = git.Repo(gitScript.directory())
    o = my_repo.remotes.origin
    o.fetch()
    my_repo.head.ref.set_tracking_branch(o.refs.master)
    o.pull()
    importlib.reload(gitScript)
    gitScript.client = client
    await client.send_message(message.author, "Command Set updated: " + str(gitScript.adminCommandsList.keys()))
    return

@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('Loading AuthUsers...')
    if os.path.isfile(authUserFile):
        with open(authUserFile, "r", newline = '') as authFile:
            reader = csv.reader(authFile, delimiter = ';', quotechar = '\'')
            for row in reader:
                for item in row:
                    if not item == '':
                        authUsers.append(str(item))
        print(str(authUsers))
    else:
        with open(authUserFile, "w+") as outputFile:
            print("Initializing auth file as " + authUserFile)
    if len(authUsers) == 0:
        await client.send_message(client.get_channel(botToken.home_channel), "Someone Claim Me!")

@client.event
async def on_message(message):
    if message.content.startswith(client.user.mention):
        namesize = len(client.user.mention)
        words = re.findall(r"[\w']+", message.content[namesize:])
        if message.author.id in authUsers:
            if len(words) > 0 and words[0] == 'sudo' and words[1] in gitScript.adminCommandsList.keys():
                tmp = await gitScript.adminCommandsList[words[1]](message)
            elif len(words) > 0 and words[0] in gitScript.userCommandsList.keys():
                tmp = await gitScript.userCommandsList[words[0]](message)
            elif len(words) > 0 and words[0] == 'sudo' and words[1] == "update":
                await reloadGit(message)
            else:
                tmp = await client.send_message(message.channel, "I'm sorry, " + message.author.mention + ", I can't do that.")
        elif len(authUsers) == 0 and message.channel.id == client.get_channel(botToken.home_channel).id:
            if len(words) > 0 and words[0] == "takeown":
                print ("Assigning Owner")
                with open(authUserFile, "w") as authFile:
                    writer = csv.writer(authFile, delimiter = ';',
                        quotechar = '\'', quoting = csv.QUOTE_MINIMAL)
                    authUsers.append(message.author.id)
                    writer.writerow(authUsers)
                print ("Updated AuthUsers:")
                print(str(authUsers))
                tmp = await client.send_message(message.channel, "Accepted " + message.author.mention + " as primary owner of this bot.")
        elif len(words) > 0 and words[0] in gitScript.userCommandsList.keys():
            gitScript.userCommandsList[words[0]](message)
        elif len(message.content) == len(client.user.mention): # when the message is just a mention
            tmp = await client.send_message(message.channel, "Hello, " + message.author.mention + "!")
        else:
            reply = message.author.mention + ", you do not have access to that command, or it does not exist."
            tmp = await client.send_message(message.channel, reply)
    else:
        namesize = len(client.user.mention)
        words = re.findall(r"[\w']+", message.content[namesize:])
        for word in words:
            if word in gitScript.foulMouth:
                tmp = await gitScript.send_message(message.channel, "HEY! " + message.author.mention + "WATCH YOUR LANGUAGE!")
client.run(botToken.value)
