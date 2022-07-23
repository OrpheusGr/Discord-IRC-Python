import re
import time
import logging
import discord
import asyncio
from asyncio import coroutines
import concurrent.futures
from asyncio import futures
import csv
import os
import weathermodule
weather = weathermodule
import wordcounter
word = wordcounter
import karmamodule
karma = karmamodule
checkfiles = ["usertags.txt"]
for file in checkfiles:
    if os.path.isfile(file) == False:
        open(file, 'w').close()

logging.basicConfig(level=logging.INFO)

thread_lock = None

settings = None
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
server = None
channel = None
irc = None

class Discord:
    def __init__(self, sett):
        global settings
        global thread_lock
        global userlist
        userlist = []

        settings = sett["discord"]

        if not settings["token"]:
            with thread_lock:
                print("[Discord] No token given. Get a token at https://discordapp.com/developers/applications/me")
            exit()

    def set_irc(self, ircc):
        global irc
        irc = ircc

    def set_thread_lock(self, lock):
        global thread_lock
        thread_lock = lock

    def sendtoboth(message):
        Discord.send_my_message("a", message)
        irc.send_my_message(message)

    def send_list(self):
        irclist = "Discord users with IRC role:"
        for member in server.members:
            for role in member.roles:
                if role.name == "IRC":
                    tag = Discord.reptag(member.mention, member.name)
                    print(tag)
                    if tag == member.name:
                        if member.nick:
                            tag = member.nick
                    if member.bot:
                        tag = tag + " " +  "\x03" + "00,12" + "BOT" + "\x0f"
                    irclist = irclist + "[bold] | [bold]" + tag
        if irclist == "Discord users with IRC role:":
            irc.send_my_message("No users with the IRC role found.")
            return
        Discord.send_my_message("a", "**Forwarding members that have the IRC role.**")
        irc.send_my_message(irclist)

    def send_my_message(self, message):
        global client
        global userlist
        newtags = []
        now = str(int( time.time() ))
        timestamp = "<t:" + now + ":T>"
        if message.count("\x02") % 2 != 0:
            message = message + "**"
        if message.count(chr(29)) % 2 != 0:
            message = message + "*"
        message = message.replace("\x02", "**")
        message = message.replace(chr(29), "*")
        message = message.replace("[bold]", "**")
        message = irc.stripcolors(message)
        tags = message.split()
        for word in tags:
            c = word[0]
            if c == "@":
                w = word[1:].lower()
                for pair in userlist:
                    if pair[1].lower() == w:
                        word = pair[0]
            newtags.append(word)
        message = LtoS(newtags)
        message = timestamp + " " + message
        asyncio.run_coroutine_threadsafe(send_my_message_async(message), client.loop)

    def setstatus(self):
        asyncio.run_coroutine_threadsafe(setstatus_async(1), client.loop)

    def run(self):
        global settings
        global client

        client.run(settings["token"])

    def close(self):
        global client
        global irc
        irc.set_running(False)
        asyncio.run_coroutine_threadsafe(client.close(), client.loop)

# Loads the tags from usertags.txt to a list

    def loadtags(self):
        global userlist
        userlist = []
        with open("usertags.txt", mode="r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if len(row):
                    user = row[0]
                    utag = row[1]
                    userlist.append([user, utag])

# Updates the tags in usertags.txt for safe keeping so loadtags() can do its work when the bot starts

    def updatetags(tags):
        open("usertags.txt", 'w').close()
        with open('usertags.txt', mode='a') as usertags:
            tagwriter = csv.writer(usertags, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for pair in tags:
                tagwriter.writerow(pair)

# Returns the tag for the discord name given, if there is one set, otherwise returns the name back

    def reptag(userid, mention):
        global userlist
        if len(userlist) == 0:
            return mention
        for i in userlist:
            user = i[0]
            utag = i[1]
            if userid == user:
                return utag
        return mention

# Adds a new usertag to the list, if not taken, and calls the updatetags() to save the new list in usertags.txt

    def addusertag(userid, want):
        global userlist
        updtag = ""
        newuserlist = []
        user = userid
        utag = want
        if len(userlist) == 0:
            userlist.append([userid, want])
            Discord.updatetags(userlist)
            Discord.send_my_message("a", "Your tag is set")
            return
        else:
            for i in userlist:
                user = i[0]
                utag = i[1]
                if utag == want and userid != user:
                    Discord.send_my_message("a", "Oops! Try another tag, this one's taken!")
                    return
                elif (utag == want and userid == user) or (utag != want and userid == user):
                    updtag = "updated"
        if updtag != "updated":
            updtag = "set"
        both = [userid, want]
        for i in userlist:
            if i[0] != userid:
                newuserlist.append(i)
        newuserlist.append(both)
        userlist = newuserlist
        Discord.updatetags(userlist)
        Discord.send_my_message("a", "Your tag is %s" % (updtag))

    def discstrip(m):
        m = m.replace("**", "")
        m = m.replace("*", "")
        m = m.replace("_", "")
        return m

def ircdressup(m):
    m = m.replace("**", "\x02")
    m = m.replace("`", " ")
    m = m.replace("*", chr(29))
    return m

def LtoS(s):
    string = " "
    return (string.join(s))

async def setstatus_async(a):
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="IRC and Discord"))

async def send_my_message_async(message):
    await channel.send(message.strip())


@client.event
async def on_message(message):
    global settings
    global client
    global channel
    global thread_lock
    global irc
    print(message.stickers)
    mention = message.author.mention
    tag = Discord.reptag(mention, message.author.name)
    if tag == message.author.name:
        if message.author.nick:
            tag = message.author.nick
    if message.author.bot:
        tag = tag + " " +  "\x03" + "00,12" + "BOT" + "\x0f"
    #RepliesPins Start - This block checks if the message is a reply to a previous message and shows it appropriately on IRC. It also checks if a message was pinned and relays that as well.
    msgrefpin = False
    if message.type == discord.MessageType.pins_add:
        msgrefpin = True
    if message.reference:
        refurl = ""
        refid = message.reference.message_id
        refinfo = await channel.fetch_message(refid)
        print(refinfo)
        refcont = ircdressup(refinfo.clean_content.strip("\n"))
        if len(refinfo.attachments) > 0:
            refurl = refinfo.attachments[0].url
        if refcont == "":
            refcont = refurl
        refauthor = refinfo.author
        refauthorname = refauthor.name
        refauthorid = refauthor.id
        if refauthorid == message.author.id:
            refauthor = message.author
        refauthorbot = refauthor.bot
        refguild = refinfo.guild
        try:
            refauthornick = refguild.get_member(refauthorid).nick
        except:
            try:
                #catch the case where the refauthor is same as message.author
                refauthornick = refauthor.nick
            except:
                refauthornick = None
        refauthormention = refauthor.mention
        reftag = Discord.reptag(refauthor.mention, refauthorname)
        if reftag == refauthorname:
            if refauthornick != None:
                refauthorname = refauthornick
        else:
            refauthorname = reftag
        if refauthorbot:
            refauthorname = refauthorname + "\x03" + "00,12" + "BOT" + "\x0f"
        if msgrefpin == False:
            if refauthor == client.user:
                refcont = "\"" + refcont.split()[1].replace("**", "[bold]") + " " + LtoS(refcont.split()[2:15])  + "\"" + " [bold] <<< [bold]"
            else:
                refcont = "\"" + "<" + refauthorname + "> " + LtoS(refcont.split()[0:14]) + "\"" + " [bold] <<< [bold]"
        else:
            if refauthor == client.user:
                refcont = LtoS(refcont.split()[1:])
            pintoirc = "%s pinned a message: <%s> %s" % (tag, refauthorname, refcont)
            irc.send_my_message(pintoirc)
            return
    else:
        refid = 0
        refinfo = 0
        refcont = ""
        refauthor = ""
    #RepliesPins End

    #ignore check start
    ignores = settings["ignores"].split()
    userid = str(message.author.id)
    if userid in ignores:
        print("Ignoring", message.author.name, "(id:", userid + ")", "found in Ignore list")
        return
    #ignore check end

    emptycontent = 0
    content = message.clean_content.replace("\n", " ").strip()
    precontent = content
    content = ircdressup(content)
    content = content.split()
    if content == []:
        emptycontent = 1
        content = ["|"]

    # Don't reply to itself
    if message.author == client.user:
        return

    if message.channel != channel:
        return


    with thread_lock:
        print("[Discord] %s: %s" % (message.author.name, LtoS(content)))

    url = ""
    word1 = content[0]
    wordz = content[-1]
    if content[0].lower() == "!tag":
        if len(content) > 1:
            Discord.addusertag(mention, content[1])
        else:
            Discord.sendtoboth("You didn't provide a tag. Usage: !tag mytaghere")
    if len(message.attachments) > 0:
        url = message.attachments[0].url
    if (word1.startswith("_") and wordz.endswith("_")) or (word1.startswith("*") and wordz.endswith("*")):
        len2 = len(content) - 1
        if len(content) >= 2:
            content = word1[1:] + " " +  LtoS(content[1:len2]) + " " +  wordz[:-1] + " " +  url
        else:
            content = word1[1:][:-1] + " " + " " +  url
        irc.send_my_message(refcont + "\x03" + "6" + chr(29) + "* %s %s%s" % (tag, content, chr(29)))
    else:
        newname = tag[0] + "\u200b" +  tag[1:]
        newname = "\x02" + newname + "\x02"
        content = LtoS(content) + " " + url
        regexc = re.compile('<:\w*:\d*>', re.UNICODE)
        findmoji = re.findall(regexc, content)
        for moji in findmoji:
            namemoji = ":" + moji.split(":")[1] + ":"
            content = content.replace(moji, namemoji)
        content = regexc.sub("", content)
        if emptycontent == 1:
            emptycontent = 0
            irc.send_my_message("%s <%s> %s" % (refcont, newname, url))
            return

        splitcontent = content.split()
        if len(splitcontent) >= 1:
            if splitcontent[0] == ".tell":
                edit = ".tell " + splitcontent[1] + " (from %s on Discord) " + LtoS(splitcontent[2:])
                irc.send_my_message(edit % (newname))
                return

        irc.send_my_message("%s <%s> %s" % (refcont, newname, content))
    iskarma = karma.caller(content, message.author.name)
    if iskarma:
        Discord.sendtoboth(iskarma)
    isweather = weather.caller(content, [message.author.name, message.author.mention])
    if isweather[0] == "error":
        Discord.sendtoboth("Error: " + isweather[1])
    elif isweather[0] == "success":
        Discord.sendtoboth(isweather[1])
    stripcontent = Discord.discstrip(precontent).split()
    isword = word.caller(message.author.name, stripcontent)
    if isword[0] == "success":
        Discord.sendtoboth(isword[1])
    elif isword[0] == "error":
        Discord.sendtoboth("Error: " + isword[1])
    botops = settings["botops"].split()
    NameIsBotOp = 0
    kickban = 0
    for op in botops:
        if userid == op:
            NameIsBotOp = 1
    if NameIsBotOp:
        NameIsBotOp = 0
        if content[0] in ["!kick", "!kickban", "!kb"]:
            cmd = content[0]
            if cmd == "!kickban" or cmd == "!kb":
                kickban = 1
            if len(content) < 2:
                Discord.send_my_message("a", "You didn't provide a nick. USAGE: !kick nick [reason]")
                return
            elif len(content) >= 2:
                if len(content) < 3:
                    kreason = "(Discord/" + message.author.name + ")" + " " + "No reason given"
                else:
                    kreason = "(Discord/" + message.author.name + ")" + " " + LtoS(content[2:])
                knick = content[1]
                print(kreason, knick)
                irc.kicknick(knick, kreason, kickban)
            #return
    if content[0] == "!nicklist":
        Discord.send_my_message("a", irc.nicklist())
        return
    if userid == settings["botowner"]:
        if content[0] == "!cutrelay":
            await client.close()
            return



@client.event
async def on_ready():
    global server
    global channel
    global thread_lock

    with thread_lock:
        print("[Discord] Logged in as:")
        print("[Discord] " + client.user.name)
        print("[Discord] " + str(client.user.id))

        if len(client.guilds) == 0:
            print("[Discord] Bot is not yet in any server.")
            await client.close()
            return

        if settings["server"] == "":
            print("[Discord] You have not configured a server to use in settings.json")
            print("[Discord] Please put one of the server IDs listed below in settings.json")

            for server in client.guilds:
                print("[Discord] %s: %s" % (server.name, server.id))

            await client.close()
            return

        findServer = [x for x in client.guilds if str(x.id) == settings["server"]]
        if not len(findServer):
            print("[Discord] No server could be found with the specified id: " + settings["server"])
            print("[Discord] Available servers:")

            for server in client.guilds:
                print("[Discord] %s: %s" % (server.name, server.id))

            await client.close()
            return

        server = findServer[0]

        if settings["channel"] == "":
            print("[Discord] You have not configured a channel to use in settings.json")
            print("[Discord] Please put one of the channel IDs listed below in settings.json")

            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    print("[Discord] %s: %s" % (channel.name, channel.id))

            await client.close()
            return

        findChannel = [x for x in server.channels if str(x.id) == settings["channel"] and x.type == discord.ChannelType.text]
        if not len(findChannel):
            print("[Discord] No channel could be found with the specified id: " + settings["server"])
            print("[Discord] Note that you can only use text channels.")
            print("[Discord] Available channels:")

            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    print("[Discord] %s: %s" % (channel.name, channel.id))

            await client.close()
            return

        channel = findChannel[0]

