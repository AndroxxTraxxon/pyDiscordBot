"""

@author: David Culbreth


"""

import discord
import json
import os
import random
import pprint
import botToken
import botUtils as utils
from botUtils import getCommandParameters

global client
global muted
defaultSettings = {
    "admins": [],
    "protected_fields": ["admins", "protected_fields", 
                         "adventure_channels", "adventure_commands"],
    "adventure_channels": [],
    "adventure_commands": dict(),
    "greetings": ["Hey, I'm awake!", "Reporting for duty, Sir!", "Hello!"],
    "greetings_leaving": ["Signing off!", "Good night!", "See you later!"]
    }

global settings
try:
    settings
except NameError:
    settings = None
global client
try:
    client
except NameError:
    client = None
    

def loadSettings():
    global settings
    try:
        with open(botToken.settingsPath, "r") as settingsFile:
            try:
                settings = defaultSettings.copy()
                settings.update(json.load(settingsFile))
            except json.decoder.JSONDecodeError:
                print("File {0} is not properly JSON formatted.\nUsing default settings...".format(botToken.settingsPath))
                storeSettings()
    except FileNotFoundError:
        print("File {0} Not Found. Using default settings...".format(botToken.settingsPath))
        storeSettings()

def storeSettings(verbose = False):
    global settings
    
    if settings is None:
        if verbose: print("Settings undefined. Using default settings...")
        settings = dict(defaultSettings)
    with open(botToken.settingsPath, "w+") as settingsFile:
        if verbose: 
            print("Saving current settings to {0}:".format(botToken.settingsPath))
            pprint.pprint(settings)
        json.dump(settings, settingsFile)
    if verbose:print("Settings save complete.")

async def greet():
    await client.send_message(client.get_channel(botToken.home_channel), random.choice(settings["greetings"]))
        
async def disp(message:discord.Message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global settings
    params = utils.getCommandParameters(message, "disp")
    if len(params) == 0:
        await client.send_message(message.channel, "Ummm... what to display...?")
    else:
        try:
            if params[0] not in settings["protected_fields"]:
                await client.send_message(message.channel, pprint.pformat(settings[params[0]], indent=4))
            elif message.author.id in settings["admins"]:
                if message.channel != message.author:
                    await client.send_message(message.channel, "Protected information sent in private message.")
                await client.send_message(message.author, pprint.pformat(settings[params[0]], indent=4))
            else:
                await client.send_message(message.channel, "{0} is not authorized to view `{1}`".format(message.author.mention))
        except:
            await client.send_message(message.channel, "I don't know what `{0}` is...".format(params[0]))
    return

async def config(message:discord.Message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global settings
    params = getCommandParameters(message, "config")
    if len(params) < 2:
        await client.send_message(message.channel, "More info required for config")
        await client.send_message(message.author, "Usage: `@Mention config key[.subkey[.subkey[...]]] value (number, string, or list)` ")
        return
    if params[0] in settings["protected_fields"] and message.author.id not in settings["admins"]:
        await client.send_message(message.author, "You do not have permission to modify {0}".format(params[0]))
        return
    newValue = None
    """Evaluate the new value to store"""
    if len(params) > 2 or params[1] == "list":
        newValue = list()
        if len(params) > 2:
            for x in range(1,len(params)):
                newValue.append(params[x])
    elif params[1] == "obj":
        newValue = dict()
    else:
        newValue = params[1]
    
    """Determine which parameter to modify"""
    if params[0].find('.') > 0:
        paramChain = params[0].split('.')
    else:
        paramChain = [params[0]]
    setting_to_change = settings
    lastKey = paramChain[len(paramChain)-1]
    for x in range(len(paramChain)-1):
        try:
            key = int(paramChain[x])
        except ValueError:
            key = paramChain[x]
        try:
            setting_to_change = setting_to_change[key]
        except:
            await client.send_message(message.channel, "Config Failed: KeyError or ValueError, or non-iterable setting")
            return
    try:
        setting_to_change[lastKey] = newValue
        await client.send_message(message.channel, "Config Successful: {0} = {1}".format(params[0], setting_to_change[lastKey]))
    except KeyError|ValueError:   
        if lastKey == '*' and isinstance(setting_to_change, list):
            setting_to_change.append(newValue)
            await client.send_message(message.channel, "Config Successful: {0} = {1}".format(params[0][:-2], setting_to_change))
        else:
            await client.send_message(message.channel, "Config Failed: KeyError or ValueError, or non-iterable setting")     

async def mute(message:discord.Message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global muted
    muted = True
    tmp = await client.send_message(message.channel, "... hmph ... (now replying to all messages privately)")
    return tmp

async def unmute(message:discord.Message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global muted
    muted = False
    tmp = await client.send_message(message.channel, "Ahhh, Freedom! (now replying to all messages in the channel)")
    return tmp

async def test(message:discord.Message):
    """
    @usage: `test`
    @param message: [discord.Message] the message containing the command
    """
    tmp = await client.send_message(message.channel, "Testing, 1, 2, 3!")
    return tmp

async def sleep(message:discord.Message):
    """
    @summary: Gracefully closes the application, closing connections and saving settings
    @usage: `sleep`
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    await client.send_message(message.channel, random.choice(settings["greetings_leaving"]))
    await client.close()
    storeSettings()
    print("Gracefully closing Discord bot...")
    return

async def roll(message:discord.Message):
    """
    @usage: `roll ndm [qdp [rds]]` for `n`,`q`,`p` for number of dice rolled
    and `m`,`p`,`s` for number of sides on the dice
    Example: `roll 2d8` (2 x 8-sided die)
    Example: `roll 3d6 5d4 1d20` (3x 6-sided die, 5x 4-sided die, 1x 20-sided die)
    @summary: Rolls a set of dice a given number of times and returns the set of rolls, 
    as well as its total value.
    @param message: [discord.Message] the message containing the command
    """
    await client.send_typing(message.channel)
    params = utils.getCommandParameters(message, "roll")
    if len(params) > 0:
        rollValues = dict()
        for rollset in params:
            try:
                rollCount, faces, = (max(1, int("0"+x)) for x in rollset.split("d"))
                if rollValues.get(faces) is None:
                    rollValues[faces] = list()
                for rollNo in range(rollCount):
                    rollValues[faces].append(random.randint(1, faces))
            except:
                await client.send_message(message.channel, "Not sure what `{0}` is...".format(rollset))
                await client.send_typing(message.channel)
                
                
        if len(rollValues) > 0:
            total = sum([sum(values) for values in rollValues.values()])
            await client.send_message(message.channel, 
                                      "You rolled: \n{0}\n Total: {1}".format(pprint.pformat(rollValues, indent=4), str(total)))
        else:
            await client.send_message(message.channel, "Give me some dice!")
    else:
        await client.send_message(message.channel, "Give me some dice!")
        
async def hmmm(message:discord.message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global hmmCount
    try:
        hmmCount += 1
    except:
        hmmCount = 1
    if hmmCount % 5 == 0:
        await client.send_message(message.channel, "There seems to be a lot of hmm-ing and haw-ing around here...")
    else:
        await client.send_message(message.channel, "hmmm, indeed...")
            
async def addAuthUser(message:discord.Message):
    """
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global settings
    try:
        message.mentions.remove(client.user)
    except ValueError:
        pass
    for mention in message.mentions:
        if (not mention.id == client.user.id
            and mention.id not in settings["admins"]):
            settings["admins"].append(mention.id)
    storeSettings()
    if len(message.mentions) > 0:
        await client.send_message(message.channel, "The Following users have been made admin:\n " + str([user.mention for user in message.mentions]))
        print("AuthUsers Updated:")
        print(str(settings["admins"]))
    else:
        await client.send_message(message.channel, "There was no user to authorize!")

async def removeAuthUser(message:discord.Message):
    """
    @usage
    @param message: [discord.Message] the message containing the command
    @return: void
    """
    global settings
    try:
        message.mentions.remove(client.user)
    except ValueError:
        pass
    for mention in message.mentions:
        try:
            settings["admin"].remove(mention.id)
        except KeyError:
            pass
    storeSettings()
    message.mentions.remove(client.user.id)
    if len(message.mentions) > 0:
        await client.send_message(message.channel, "The following users no longer have admin privileges:\n " + str([user.mention for user in message.mentions]))
        print("AuthUsers Updated:")
        print(str(settings["admins"]))
    else:
        await client.send_message(message.channel, "There was no user to authorize!")

async def dispHelp(message:discord.Message):
    """
    @usage: `help [command]`
    @summary: Displays admin functions, or usage of a specified admin command, if one is provided
    @param message: [discord.Message] the message containing the command
    """
    params = utils.getCommandParameters(message, "help", includeCommandName=True)
    if len(params) > 1 and (params[1] in commandsList.keys() or (params[1] in commandsListAdmin.keys() and message.author.id in settings["admins"])):
        if params[1] in commandsList.keys():
            cmd_docstring = commandsList[params[1]].__doc__
        else:
            cmd_docstring = commandsListAdmin[params[1]].__doc__
        tagStrings = cmd_docstring.split('@')
        usageString = None
        summaryString = None
        for tag in tagStrings:
            if tag.startswith("usage"):
                usageString = tag[len("usage"):]
            elif tag.startswith("summary"):
                summaryString = tag[len("summary"):]
        if usageString is not None:
            await client.send_message(message.channel, "Usage {0}".format(usageString))
            if summaryString is not None:
                await client.send_message(message.channel, "Summary {0}".format(summaryString))
        else:
            await client.send_message(message.channel, "Documentation {0}".format(cmd_docstring)) 
              
    else:
        await client.send_message(message.channel,"Valid commands for this bot: "+ str(commandsList.keys()))

async def dispAdminHelp(message:discord.Message):
    """
    @usage: `sudo help [command]`
    @summary: Displays admin functions, or usage of a specified admin command, if one is provided
    @param message: [discord.Message] the message containing the command
    """
    params = utils.getCommandParameters(message, "help", includeCommandName=True)
    if len(params) > 1 and (params[1] in commandsList.keys() or (params[1] in commandsListAdmin.keys() and message.author.id in settings["admins"])):
        if params[1] in commandsListAdmin.keys():
            cmd_docstring = commandsListAdmin[params[1]].__doc__
        else:
            cmd_docstring = commandsList[params[1]].__doc__
        tagStrings = cmd_docstring.split('@')
        usageString = None
        summaryString = None
        for tag in tagStrings:
            if tag.startswith("usage"):
                usageString = tag[len("usage"):]
            elif tag.startswith("summary"):
                summaryString = tag[len("summary"):]
        if usageString is not None:
            await client.send_message(message.channel, "Usage {0}".format(usageString))
            if summaryString is not None:
                await client.send_message(message.channel, "Summary {0}".format(summaryString))
        else:
            await client.send_message(message.channel, "Documentation {0}".format(cmd_docstring)) 
              
    else:
        await client.send_message(message.channel,"Valid commands for this bot: "+ str(commandsList.keys()))
        
async def dispDoc(message:discord.Message):
    """
    @usage: `doc <command>`
    @summary: Displays full documentation provided for any given function
    @param message: [discord.Message] the message containing the command
    """
    params = utils.getCommandParameters(message, "doc", includeCommandName=True)
    if len(params) > 1 and (params[1] in commandsList.keys() or (params[1] in commandsListAdmin.keys() and message.author.id in settings["admins"])):
        if params[1] in commandsList.keys():
            cmd_docstring = commandsList[params[1]].__doc__
        else:
            cmd_docstring = commandsListAdmin[params[1]].__doc__
        await client.send_message(message.channel, cmd_docstring)
    elif len(params) > 1 and (params[1] in commandsListAdmin.keys() and message.author.id not in settings["admins"]):
        await client.send_message(message.channel, "You do not have the access to use `{0}".format(params[1]))
    else:
        if len(params) > 1:
            await client.send_message(message.channel,"`{0}` is not a valid command.".format(params[1]))
        else:
            await client.send_message(message.channel,"`doc` usage {0}".format(utils.getDocTag(dispDoc, "usage")))

commandsListAdmin = {
    "sleep": sleep,
    "op": addAuthUser,
    "deop": removeAuthUser,
    "help": dispAdminHelp,
    "disp": disp
}

commandsList = {
    "help"  : dispHelp,
    "test"  : test,
    "mute"  : mute,
    "unmute": unmute,
    "roll"  : roll,
    "hm"    : hmmm,
    "hmm"   : hmmm,
    "hmmm"  : hmmm,
    "hmmmm" : hmmm,
    "set"   : config,
    "doc"   : dispDoc,
}


def directory():
    return os.path.dirname(os.path.realpath(__file__))
