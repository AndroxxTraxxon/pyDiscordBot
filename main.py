import discord
import asyncio
import csv
import re
import os
import importlib
import git
import gitScript

client = discord.Client()
gitScript.client = client
authUsers = []
authUserFile = "authUsers.csv"
token = 'MzM5NjI0Mjg0NjgxMTQyMjc0.DFmw9g.4s0a1KbjZcY8Y0Ju1TMMEZ2SpWU'
home_channel = "339622824631205899"

async def reloadGit(message):
    await client.send_message(message.channel, "Updating Command Set...")
    my_repo = git.Repo(gitScript.directory())
    o = my_repo.remotes.origin
    o.fetch()
    my_repo.head.ref.set_tracking_branch(o.refs.master)
    o.pull()
    importlib.reload(gitScript)
    gitScript.client = client
    await client.send_message(message.channel, "Command Set updated: " + str(gitScript.commandsList.keys()))
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
        await client.send_message(client.get_channel(home_channel), "Someone Claim Me!")

@client.event
async def on_message(message):
    if message.content.startswith(client.user.mention):
        namesize = len(client.user.mention)
        if message.author.id in authUsers:
            words = re.findall(r"[\w']+", message.content[namesize:])
            if len(words) > 0 and words[0] == 'sudo' and words[1] in gitScript.commandsList.keys():
                tmp = await gitScript.commandsList[words[1]](message)
            elif len(message.content) == len(client.user.mention):
                tmp = await client.send_message(message.channel, "Hello, " + message.author.mention + "!")
            elif len(words) > 0 and words[0] == 'sudo' and words[1] == "update":
                await reloadGit(message)
            else:
                tmp = await client.send_message(message.channel, "I'm sorry, " + message.author.mention + ", I can't do that.")
        elif len(authUsers) == 0 and message.channel.id == client.get_channel(home_channel).id:
            words = re.findall(r"[\w']+", message.content[namesize:])
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

        else:
            reply = message.author.mention + ", you are not authorized to control this bot."
            tmp = await client.send_message(message.channel, reply)

client.run(token)
