'''
Created on Jul 14, 2018

@author: David Culbreth
'''

import discord
import re
from typing import Callable, NoReturn

def getCommandParameters(message:discord.Message, commandName:str, includeCommandName:bool = False) -> list:
    """
        @param message: [discord.Message] the message object containing the command
        @param commandName: [str] the name of the command as a string
        @return a list of parameters, as delimited by whitespace. 
                The first parameter is the name of the command.
    """
    return re.findall(r"[\w']+", message.content[message.content.find(commandName)+(0 if includeCommandName else len(commandName)):])

def getWords(inputString:str) -> list:
    return re.findall(r"[\w']+", inputString)

def getDocTag(func:Callable[[discord.Message], NoReturn], tag:str) -> str:
    if func.__doc__ is not None:
        docString = func.__doc__
        stringTags = docString.split('@')
        for string in stringTags:
            if string.startswith(tag):
                return string[len(tag):]
    return None