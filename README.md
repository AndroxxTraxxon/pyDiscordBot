# pyDiscordBot Version 0.2.0


<ci coming soon>
A basic 
 >By [@AndroxxTraxxon](https://github.com/AndroxxTraxxon) - David Culbreth

## Requirements
 - Python 3.6+ (NOT COMPATIBLE WITH 3.5... I used type hints. removing those should get it running in 3.x)
 - [discord.py](https://github.com/Rapptz/discord.py)
 - An [Application/Bot Token from Discord](https://discordapp.com/developers/docs/intro)


## Getting Started
Assuming you have Python and discord.py installed, and this repo downloaded... 
 - make a copy of `botToken.py.sample`, and rename it to `botToken.py` 
   - *(the .gitignore keeps this out to help hide your secret token.)*
 - Inside `botToken.py`, add the string value of your token from the discord developer API as the value:
   - `value = "kajhsbgdfkjhas.aksdhfj.akjsdhg-fkuywe"` <== not a real value, put yours in like that.
 - Your bot needs a default channel to speak up on. add `home_channel` as the channel id of the desired home channel for the bot.
   - Note that this is where the bot will output any error messages, etc. 
     So don't make this a channel that people regularly talk on. I made a new one called `bot_spam` just for the bot.
   - This **channel id** can be retrieved by right clicking on the channel inside the Discord application,
     in the list of channels on the server.
   - `home_channel = "209384570293574987"` <== also not a real value, but your channel id will look like this.
   - Note that it is a ***string*** value. that is what the Discord API is expecting. Changing it to an int may have unexpected results.
     
## Running the bot
To run the bot in the console, move to the `src` directory, and run the `main.py` file with Python 3.6.


```console
> cd \path\to\pyDiscordBot\src
\path\to\pyDiscordBot\src> python .\main.py
```
The bot should start running, and it will look something like this...
```
Initializing...
Logged in as <Your Bot Name> <Your Bot UserID>
Loading settings...
```
At this point, the bot should appear as online within Discord. 

## Using commands
This bot can be used by 
## Adding new commands


## Hot-Swapping Functions
A core functionality of this bot is that its command set can be updated while the bot is still running. 
the command to do so is to write `.\sudo update` in the command line. 
This will trigger a `git fetch & git pull` by default (use ` --local` to just update with local changes) and reload the botFunctions
