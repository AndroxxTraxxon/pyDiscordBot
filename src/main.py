"""

@author: David Culbreth

"""

# Discord core required files
import discord
import traceback
# import asyncio

# Files for text parsing
import re

# Libraries for Git-Enabled Updating
import importlib
import git
import botFunctions
import botUtils as utils

# The botToken is used to uniquely identify your bot.
import botToken  # You write this file! copy from botToken.py.sample.
print("Initializing...")
client = discord.Client()
botFunctions.client = client


@client.event
async def on_ready():
    print('Logged in as', client.user.name, client.user.id)
    print('Loading settings...')
    botFunctions.loadSettings()
    print('Settings loaded')
    await botFunctions.greet()
    print('{0} is open for service'.format(client.user.name))
    if len(botFunctions.settings["admins"]) == 0:
        print("Waiting for someone to claim the bot at {0} -> {1}".format(client.get_channel(botToken.home_channel).server.name,
                                                                          client.get_channel(botToken.home_channel).name))
        await client.send_message(client.get_channel(botToken.home_channel),
                                  "Someone Claim Me! (\"@Mention sudo takeown\")")

async def reloadFunctions(message:discord.Message):
    await client.send_message(message.channel, "Updating Command Set...")
    params = utils.getCommandParameters(message, "update")
    if "local" not in params:
        if "verbose" in params: await client.send_message(message.channel, "Performing git fetch/pull...")
        my_repo = git.Repo(botFunctions.directory() + "\..")
        o = my_repo.remotes.origin
        o.fetch()
        my_repo.head.ref.set_tracking_branch(o.refs.master)
        o.pull()
        del o
        del my_repo
        if "verbose" in params: await client.send_message(message.channel, "git pull successful.")
    else:
        if "verbose" in params: await client.send_message(message.channel, "Using local botFunctions...")
    await client.send_message(message.channel, "Reloading Command Set...")
    importlib.reload(botFunctions)
    importlib.reload(utils)
    botFunctions.client = client
    if "verbose" in params: await client.send_message(message.channel,
                                                      "Command Set updated: "
                                                      + str(list(botFunctions.commandsList.keys())))
    if "verbose" in params: await client.send_message(message.author,
                                                      "Admin Command Set Updated: "
                                                      + str(list(botFunctions.commandsListAdmin.keys())))
    await client.send_message(message.channel, "Commands updated successfuly.")

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
    
    commandWords = None
    if (myMention is not None and message.content.startswith(myMention)
        or message.channel.is_private 
        or message.content.startswith(botToken.callingCard)):
        if myMention is not None and message.content.startswith(myMention):
            """when the bot is called by name/mention"""
            commandWords = re.findall(r"[\w']+", message.content[len(myMention):])
        elif message.content.startswith(botToken.callingCard):
            """when the bot is called by callingCard"""
            commandWords = re.findall(r"[\w']+", message.content[len(botToken.callingCard):])
        else:
            """when the bot is in private channel, and not called by anything"""
            commandWords = re.findall(r"[\w']+", message.content)
            
        if len(commandWords) > 0:
            if commandWords[0].lower() == "sudo":
                commandWords.pop(0)  # remove "sudo" from commandWords list.
                if message.author.id in botFunctions.settings["admins"]:

                    """
                    since "sudo" was written, we check the admin commandsList
                    first, then the normal one.
                    """
                    if commandWords[0] in botFunctions.commandsListAdmin.keys():
                        await botFunctions.commandsListAdmin[commandWords[0]](message)
                    elif commandWords[0] in botFunctions.commandsList.keys():
                        await botFunctions.commandsList[commandWords[0]](message)
                    elif commandWords[0].lower() == 'update':
                        await reloadFunctions(message)
                    else:
                        reply = message.author.mention + ", that is not a known command."
                elif len(botFunctions.settings["admins"]) == 0 and commandWords[0] == 'takeown':
                    
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
                    reply = "{0}, you are not permitted to use `sudo`.".format(message.author.mention)
                """
                since "sudo" was not written,
                we will check the normal commandsList first.
                """
            elif commandWords[0].lower() in botFunctions.commandsList.keys():
                await botFunctions.commandsList[commandWords[0].lower()](message)
            elif commandWords[0][0:min(5, len(commandWords[0]))].lower() in botFunctions.commandsList.keys():
                await botFunctions.commandsList[commandWords[0].lower()[0:min(5, len(commandWords[0]))]](message)
            elif (commandWords[0].lower() in botFunctions.commandsListAdmin.keys()):
                if message.author.id in botFunctions.settings["admins"]:
                    await botFunctions.commandsListAdmin[commandWords[0].lower()](message)
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
        await client.send_message(message.channel, reply)


@client.event        
async def on_error(event, *args, **kwargs):
    await client.send_message(client.get_channel(botToken.home_channel), "An Error Occurred:")
    await client.send_message(client.get_channel(botToken.home_channel), "```" + traceback.format_exc() + "```")
        
if __name__ == "__main__":
    client.run(botToken.value)
