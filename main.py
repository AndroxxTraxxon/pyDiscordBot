# Discord core required files
import discord
# import asyncio

# Files for text parsing
import csv
import re

# Libraries for Git-Enabled Updating
import os
import importlib
import git
import gitScript

# The botToken is used to uniquely identify your bot.
import botToken  # You write this file! copy from botToken.py.sample.
print("Initializing...")
authUsers = []
authUserFile = "authUsers.csv"
client = discord.Client()
gitScript.initSequence(client, authUserFile, authUsers)
messages = []


async def reloadGit(message):
    await client.send_message(message.channel, "Updating Command Set...")
    my_repo = git.Repo(gitScript.directory())
    o = my_repo.remotes.origin
    o.fetch()
    my_repo.head.ref.set_tracking_branch(o.refs.master)
    o.pull()
    del o
    del my_repo
    importlib.reload(gitScript)
    gitScript.client = client
    await client.send_message(message.channel,
                              "Command Set updated: "
                              + str(gitScript.commandsList.keys()))
    await client.send_message(message.channel,
                              "Admin Command Set Updated"
                              + str(gitScript.commandsListAdmin.keys()))
    return


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------------------')
    print('Loading AuthUsers...')
    if os.path.isfile(authUserFile):
        with open(authUserFile, "r", newline='') as authFile:
            reader = csv.reader(authFile, delimiter=';', quotechar='\'')
            for row in reader:
                for item in row:
                    if not item == '':
                        authUsers.append(str(item))
        print(str(authUsers))
    else:
        open(authUserFile, "w+")
        print("Initializing auth file as " + authUserFile)
    if len(authUsers) == 0:
        await client.send_message(client.get_channel(botToken.home_channel),
                                  "Someone Claim Me!")


@client.event
async def on_message(message):
    reply = ""
    # if message.content.startswith(client.user.mention):
    myMention = message.server.get_member(client.user.id).mention
    if message.content.startswith(myMention):

        namesize = len(client.user.mention)
        words = re.findall(r"[\w']+", message.content[namesize:])
        if len(words) > 0:
            if words[0].lower() == "sudo":
                words.pop(0)  # remove "sudo" from words list.
                if message.author.id in authUsers:

                    """since "sudo" was written, we check the admin commandsList
                    first, then the normal one."""
                    if words[0] in gitScript.commandsListAdmin.keys():
                        await gitScript.commandsListAdmin[words[0]](message)
                    elif words[0] in gitScript.commandsList.keys():
                        await gitScript.commandsList[words[0]](message)
                    elif words[0].lower() == 'update':
                        await reloadGit(message)
                    else:
                        reply = message.author.mention + ", that is not a known\
                         command."
                elif len(authUsers) == 0 and words[0] == 'takeown':
                    """ Assign ownership to the first person who writes
                    "@Mention sudo takeown" """
                    print("Assigning Owner")
                    with open(authUserFile, "w") as authFile:
                        writer = csv.writer(authFile, delimiter=',',
                                            quotechar='\'',
                                            quoting=csv.QUOTE_MINIMAL)
                        authUsers.append(message.author.id)
                        writer.writerow(authUsers)
                    print("Updated AuthUsers:")
                    print(str(authUsers))
                    tmp = await client.send_message(message.channel,
                                                    "Accepted " +
                                                    message.author.mention +
                                                    " as primary owner of \
                                                    this bot.")
                else:
                    reply = message.author.mention
                    reply += ", you are not permitted to use"
                    reply += " Super User commands."
            """since "sudo" was not written,
            we will check the normal commandsList first."""
            elif words[0] in gitScript.commandsList.keys():
                await gitScript.commandsList[words[0]](message)
            elif words[0] in gitScript.commandsListAdmin.keys():
                if message.author.id in authUsers:
                    await gitScript.commandsListAdmin[words[0]](message)
                else:
                    reply = message.author.mention + ", you are not permitted \
                    to use Super User commands."
            else:
                reply = message.author.mention +
                ", that is not a known command."
        else:
            reply = "What's up, " + message.author.mention + "?"
    else:
        # add message to data tracking for TensorFlow
        # messages[message.channel].append(message.content)
        return
    if not reply == "":
        tmp = await client.send_message(message.channel, reply)
client.run(botToken.value)
