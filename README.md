# Discord-IRC-Python
Multi-channel bot that syncs messages between Discord and IRC purely written in Python

## Requirements
A minimum of Python 3.5

## Installation
Install the following python libraries using pip:

- irc
- discord.py
- (Optional for the weather module to work) requests (https://pypi.org/project/requests/)

Download the code from this repository, then copy `settings.example.json` to `settings.json` and configure it.

Add a new application and bot user to your Discord account, (on the Discord Developer Portal https://discord.com/developers/applications)  then invite your bot to a server you manage:

https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=3072  
(change CLIENT_ID to your application's client_id)

## Features
- Multi channel. You can set your bot to work on sets of IRC and Discord channels.
-   A channel set should be put in the channelsets section of settings.json. The item should be the Discord channel's id and its value should be the IRC channel name. ("92929388305": "#potatos")  That way you can have diff discord channels be relayed to diff IRC channels and vice versa.

-   (For example you could make a Discord channel for every IRC channel and have some sort of "link" between your Discord and IRC server. Just an example.)  

- Simple SSL support to connect the bot to IRC using SSL, if you wish to. (On/Off settings in settings.json irc section, don't forget to set the port to an ssl enabled one listed on the network you are connectiing it to.)

- I have tried to make the bot relay the content in a way that looks as close as possible to actual IRC.
- The content of messages is relayed as is, with small adjustments to show custom emoji names on IRC instead of the raw version.

- You can mention Discord users from within IRC (only if they've set a custom tag word, which will also show as their Discord "name" on IRC) To set a custom tag do !tag \<tag> on a discord channel that's being relayed. (without the <>) (e.g If i set my tag to "Orf" my relayed messages will show me as Orf instead of my real Discord name and you can then use @Orf on IRC  to mention me on Discord)

- All relayed messages/events (channel messages, actions, joins, parts, quits, kicks) are relayed with a timestamp (Discord feat) that is seen by each Discord user as their own time, to enchance the feeling of classic IRC.

- Relayed Replies. When a Discord user replies to a Discord message the replied message and the reply are shown in IRC for clarity of IRC users. You may also reply to a relayed message which will be shown to IRC without the prefixed timestamp (again for clarity)

- Discord Botop commands (!kick, !kickban/!kb) To make use of them your Discord user id has to be in the botops value in settings.json (discord section). You may add multiple user id's if you want more than one person to have access to these commamds. (Needless to say that you should give access with caution if you don't want people getting banned from your IRC channel(s).) The bot needs any level of ops/halfops to carry out these commands otherwise nothing will happen. You also have the option to give your bot ChanServ access/flags to use kick/kickban (r flag on most services) and set chanservkick to 1 in settings.json so the bot doesn't have to be opped but kick/kickban through Chanserv.

- Weather Module. This module is fully written by yours trully and can fetch current weather and forecast info for your desired location. You can also set up a default location that is saved under your nick, host or your discord user id so that you don't have to input it everytime. (+setweather <location>) See more info on what you need to make it work in the below section.

- IRC services identification. You can make the bot identify (not register*) with NickServ to your desired account (doesn't have to be the bot's nick). Help is given in settings.json (*You need to use a preexisting account)

- Word counter module. This is a simple module where you can add words to a list and the bot will keep count of how many times those words are sent in messages, on IRC and Discord. (commands: +wordlist/+listwords +delword +addword +wordcount/+wcount

- Karma module, inspired by the Karma plugin of SupyBot/Limnoria this module lets you give or take Karma from, basically words which can be IRC nicks or the word UwU. Simply do UwU-- or UwU++ Orfeas++ bananas-- etc. Use +karma <word> to see the karma of someone/something, if you don't provide a word it will show the karma for your nick.

## Running and setting up details
Just launch the bot using `python3 main.py`.
- To quit the bot, type `!cutrelay` in the IRC or Discord channel. (Your IRC nick or Discord id must be set as "botowner" in settings.json irc or discord section respectively.)
- If you want to make use of the weather module you need an AccuWeather API key(s) which you can obtain for free in https://developer.accuweather.com/  Once you've done that you need to input your key in settings.json in the misc section ("apikey": "your key here")

## Licence

### Running the bot
- If you use this bot, you must let the users in the Discord and IRC channels know that their messages are being sent to one-another. The contributors to this repositories are not responsible for anything done by the program.  
- Use the send_nick_list settings with caution. Some Discord users may not want their nicks showcased in IRC channels and vice versa. If you do enable the discord side send_nick_list, you need to create an "IRC" role and give it to anyone that wants to be shown on IRC, if such role doesn't exist the bot will not send any list.

### Developing
You may change the code from this repository, but you have to credit this repository.  
You can fork and make your own improvements, or check out the forks of other people.
