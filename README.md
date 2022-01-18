# Discord-IRC-Python
Bot that syncs messages between Discord and IRC

## Requirements
A minimum of Python 3.5

## Installation
Install the following python libraries using pip:

- irc
- discord.py

Download the code from this repository, then copy `settings.example.json` to `settings.json` and configure it.

Add a new application and bot user to your Discord account, then invite your bot to a server you manage:

https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=3072  
(change CLIENT_ID to your application's client_id)

## Running
Just launch the bot using `python3 main.py`.
• To quit the bot, type `!cutrelay` in the IRC or Discord channel.
• If you want to make use of the weather module you need a AccuWeather API key whick you can obtain in https://developer.accuweather.com/  Once you've done that you need to input your key in settings.json in the misc section, in the value of "apikey"
• For the 'op' commands to work, you need to add the Discord User ID's of the users you want to allow usage. You can see someone's user ID by enabling Developer Mode in Discord Client, then simply click/tap on their Discord name and select "copy user id". Some related options are in settings.example.json
• You can make the bot identify to IRC Services, if you wish to, simple options to configure that are in settings.example.json

## Licence

### Running the bot
If you use this bot, you must let the users in the Discord and IRC channels know that their messages are being sent to one-another. The contributors to this repositories are not responsible for anything done by the program.

### Developing
You may change the code from this repository, but you have to credit this repository.  
You can fork and make your own improvements, or check out the forks of other people.
