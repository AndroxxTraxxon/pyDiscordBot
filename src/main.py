# Discord core required files
import discord
import traceback
# import asyncio

# Files for text parsing
import json
import re

# Libraries for Git-Enabled Updating
import os
import importlib
import git
import botFunctions

# The botToken is used to uniquely identify your bot.
import botToken  # You write this file! copy from botToken.py.sample.
print("Initializing...")
settingsPath = "settings.json"
client = discord.Client()
botFunctions.client = client

@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    print('Loading settings...')
    botFunctions.loadSettings()
    await botFunctions.greet()
    if len(botFunctions.settings["admins"]) == 0:
        await client.send_message(client.get_channel(botToken.home_channel),
                                  "Someone Claim Me! (\"@Mention sudo takeown\")")

async def reloadFunctions(message):
    await client.send_message(message.channel, "Updating Command Set...")
    try:
        my_repo = git.Repo(botFunctions.directory())
        o = my_repo.remotes.origin
        o.fetch()
        my_repo.head.ref.set_tracking_branch(o.refs.master)
        o.pull()
        del o
        del my_repo
    except:
        await client.send_message(message.author, "Git fetch/pull sequence failed...\n Continuing to reload module")
    importlib.reload(botFunctions)
    botFunctions.client = client
    await client.send_message(message.channel,
                              "Command Set updated: "
                              + str(list(botFunctions.commandsList.keys())))
    await client.send_message(message.author,
                              "Admin Command Set Updated: "
                              + str(list(botFunctions.commandsListAdmin.keys())))
    return

@client.event
async def on_message(message):
    if message.author == client.user:
        """ If the bot is the author, do not reply"""
        return
    reply = ""
    if message.channel.is_private:
        myMention = client.user.mention
    else:
        myMention = message.server.get_member(client.user.id).mention
        
    if (myMention is not None and message.content.startswith(myMention)) or (message.channel.is_private) or message.content.startswith(".\\"):
        namesize = 0
        if myMention is not None and message.content.startswith(myMention):
            namesize = len(client.user.mention)
        words = re.findall(r"[\w']+", message.content[namesize:])
        if len(words) > 0:
            if words[0].lower() == "sudo":
                words.pop(0)  # remove "sudo" from words list.
                if message.author.id in botFunctions.settings["admins"]:

                    """since "sudo" was written, we check the admin commandsList
                    first, then the normal one."""
                    if words[0] in botFunctions.commandsListAdmin.keys():
                        await botFunctions.commandsListAdmin[words[0]](message)
                    elif words[0] in botFunctions.commandsList.keys():
                        await botFunctions.commandsList[words[0]](message)
                    elif words[0].lower() == 'update':
                        await reloadFunctions(message)
                    else:
                        reply = message.author.mention + ", that is not a known command."
                elif len(botFunctions.settings["admins"]) == 0 and words[0] == 'takeown':
                    
                    """ Assign ownership to the first person who writes
                    "@Mention sudo takeown" """
                    print("Assigning Owner")
                    botFunctions.settings["admins"] = list()
                    botFunctions.settings["admins"].append(message.author.id)
                    botFunctions.storeSettings()
                    print("Updated AuthUsers:")
                    print(str(botFunctions.settings["admins"]))
                    await client.send_message(message.channel, "Accepted {0}  as primary owner of this bot.".format(message.author.mention))
                else:
                    reply = "{0}, you are not permitted to use Super User commands.".format(message.author.mention)
                """
                since "sudo" was not written,
                we will check the normal commandsList first.
                """
            elif words[0].lower() in botFunctions.commandsList.keys():
                await botFunctions.commandsList[words[0].lower()](message)
            elif words[0][0:min(5, len(words[0]))].lower() in botFunctions.commandsList.keys():
                await botFunctions.commandsList[words[0].lower()[0:min(5, len(words[0]))]](message)
            elif (words[0].lower() in botFunctions.commandsListAdmin.keys()):
                if message.author.id in botFunctions.settings["admins"]:
                    await botFunctions.commandsListAdmin[words[0].lower()](message)
                else:
                    reply = message.author.mention + ", you are not permitted to use Super User commands."
            else:
                reply = message.author.mention + ", that is not a known command."
        else:
            reply = "What's up, " + message.author.mention + "?"
    else:
        # add message to data tracking for TensorFlow
        # messages[message.channel].append(message.content)
        return
    if not reply == "":
        tmp = await client.send_message(message.channel, reply)


@client.event        
async def on_error(message):
    await client.send_message(client.get_channel(botToken.home_channel), "An Error Occurred:")
    await client.send_message(client.get_channel(botToken.home_channel), "```" + traceback.format_exc() + "```")
        
if __name__ == "__main__":
    client.run(botToken.value)
