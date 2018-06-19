import discord
import json
import os
import re
import random
import pprint
import botToken

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
                print("Malformed file. Using default settings...")
                storeSettings()
    except FileNotFoundError:
        print("File Not Found. Using default settings...")
        storeSettings()

async def greet():
    await client.send_message(client.get_channel(botToken.home_channel), random.choice(settings["greetings"]))
        
def storeSettings():
    global settings
    if settings is None:
        settings = dict(defaultSettings)
    with open(botToken.settingsPath, "w+") as settingsFile:
        json.dump(settings, settingsFile)
        
async def disp(message:discord.Message):
    global settings
    params = re.findall(r"[\w']+", message.content[message.content.find("disp")+len("disp"):])
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
    global settings
    params = re.findall(r"[\w']+", message.content[message.content.find("config")+len("config"):])
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
    except:    
        if lastKey == '*' and isinstance(setting_to_change, list):
            setting_to_change.append(newValue)
            await client.send_message(message.channel, "Config Successful: {0} = {1}".format(params[0][:-2], setting_to_change))
        else:
            await client.send_message(message.channel, "Config Config Failed: KeyError or ValueError, or non-iterable setting")
                
async def mute(message:discord.Message):
    global muted
    muted = True
    tmp = await client.send_message(message.channel, "... hmph ... (now replying to all messages privately)")
    return tmp


async def unmute(message:discord.Message):
    global muted
    muted = False
    tmp = await client.send_message(message.channel, "Ahhh, Freedom! (now replying to all messages in the channel)")
    return tmp


async def test(message:discord.Message):
    tmp = await client.send_message(message.channel, "Testing, 1, 2, 3!")
    return tmp


async def sleep(message:discord.Message):
    await client.send_message(message.channel, random.choice(settings["greetings_leaving"]))
    await client.close()
    storeSettings()
    print("Gracefully closing Discord bot...")
    return

async def roll(message:discord.Message):
    await client.send_typing(message.channel)
    params = re.findall(r"[\w']+", message.content[message.content.find("roll")+len("roll"):])
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
    await client.send_message(message.channel,"Valid commands for this bot: "+ str(commandsList.keys()))


async def dispAdminHelp(message:discord.Message):
    await client.send_message(message.author,"Valid admin commands for this bot: "
                        + str(list(commandsListAdmin.keys()) + ["update"]))

commandsListAdmin = {
    "sleep": sleep,
    "authorize": addAuthUser,
    "auth": addAuthUser,
    "op": addAuthUser,
    "deauth": removeAuthUser,
    "deauthorize": removeAuthUser,
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
    "config": config
}


def directory():
    return os.path.dirname(os.path.realpath(__file__))
