import irc.bot
import ssl
import re
import time
import weathermodule
weather = weathermodule
import wordcounter
word = wordcounter

# Thanks to Alak Yadav for text_wrapper.py that solved my long messages problems -Orfeas
# https://gist.githubusercontent.com/alakyadav/e3e33549b0a290cabcaee9686753fe03/raw/0dfe99803988adc0aef60cdefc5ba1839c000ce7/text_wrapper.py

# Based on irccat2.py and testbot.py from https://github.com/jaraco/irc

class IRC(irc.bot.SingleServerIRCBot):
    thread_lock = None
    running = True

    settings = None
    connection = None
    discord = None
    network = None
    channel = None
    global channelwho
    channelwho = []
    global warnlist
    warnlist = []
    def __init__(self, settings):
        irc.client.ServerConnection.buffer_class.encoding = "UTF-8"
        irc.client.ServerConnection.buffer_class.errors = "replace"
        ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        ssl_kwargs = {"connect_factory": ssl_factory}

        irc.bot.SingleServerIRCBot.__init__(self, [\
            (settings["irc"]["server"],\
            int(settings["irc"]["port"]))],\
            settings["irc"]["nickname"],\
            settings["irc"]["nickname"],
            **ssl_kwargs)


        self.settings = settings["irc"]

    def set_discord(self, discordc):
        self.discord = discordc

    def roll_back(self, msg, left, right):
        while right > 0 and msg[left + right] != ' ':
            right -= 1
        return right

    def split_msg(self, msg):
        limit = 480
        left = 0
        right = limit - 1

        while left + limit < len(msg):
            right = self.roll_back(msg, left, right)

            if right == 0:
                right = limit - 1
                self.connection.privmsg(channel, msg[left:left + right + 1] + "-")
            else:
                self.connection.privmsg(channel, msg[left:left + right + 1])

            left += right + 1
            right = limit

        self.connection.privmsg(channel, msg[left:len(msg)])

    def set_thread_lock(self, lock):
        self.thread_lock = lock

    def sendtoboth(self, message):
        self.send_my_message(message.replace("[bold]", "\x02"))
        self.discord.send_my_message(self.stripcolors(message.replace("[bold]", "**")))

    def send_my_message(self, message):
        message = message.replace("[bold]", "\x02")
        if len(message) >= 480:
            self.split_msg(message)
        else:
            self.connection.privmsg(channel, message.strip())
'''
    def warnkickban(self, message, nick):
        global warnlist
        global channel
        warnexcept = ["grandmom", "granddad", "elune", "skittle", "atheism", "drpoxenstein"]
        if nick.lower() in warnexcept:
            return
        warns = 0
        message = message.lower()
        message = message.split()
        badwords = ["nigger", "niger", "niggers", "nigers"]
        for word in message:
            if word in badwords:
                for pair in warnlist:
                    user = pair[0]
                    if user == nick:
                        warns = pair[1]
                        if warns == 1:
                            warnlist.remove(pair)
                            warns += 1
                            warnlist.append([nick, warns])
                        elif warns == 2:
                            kreason = "Refrain from excessive use of such terms in " + channel + " You have been warned already."
                            self.kicknick(nick, kreason, 0)
                            warnlist.remove(pair)
                            warns += 1
                            warnlist.append([nick, warns])
                        elif warns == 3:
                            kreason = "You have been warned about using such terms in here. Goodbye."
                            self.kicknick(nick, kreason, 1)
                            warnlist.remove(pair)
                            return
                if warns == 0:
                    addwarn = [nick, 1]
                    warnlist.append(addwarn)
                    self.send_my_message(nick + ": Please avoid using such terms in " + channel + ". Excessive use will lead into a ban. Respect everyone :)")
                    return
'''
    def fromhost(self, host, part):
        if iswm.match("*!*@*", host) == False:
            return None
        if part == "ident":
            return host.split("!").split("@")[0]
        if part == "identhost":
            return host.split("!")[1]
        else:
            return host


    def kicknick(self, knick, kreason, ban):
        global channel
        chanservkick = self.settings["chanservkick"]
        isnick = self.isonchan(knick)
        if isnick == "True":
            if ban == 1:
                if chanservkick == 1:
                    cskb = "KICKBAN " + channel + " " + knick + " " + kreason
                    self.connection.privmsg("ChanServ", cskb)
                    return
                bancmd = "+b " + "*!*@" + self.gethost(knick)
                self.connection.mode(channel, bancmd)
                self.connection.kick(channel, knick, kreason)
                return
            if chanservkick == 1:
                csk = "KICK " + channel + " " + knick + " " + kreason
                self.connection.privmsg("ChanServ", csk)
                return
            self.connection.kick(channel, knick, kreason)
        else:
            self.discord.send_my_message("Nick not in channel")

    def isonchan(self, target):
        global channelwho
        for pair in channelwho:
            nick = pair[0]
            if nick == target:
                return "True"
        return "False"

    def gethost(self, user):
        global channelwho
        for pair in channelwho:
            nick = pair[0]
            if nick == user:
                host = pair[1]
                return host
        return "False"

    def nicklist(self):
        global channel
        global channelwho
        y = ""
        for pair in channelwho:
            nick = pair[0]
            if y == "":
                y = "%s Nicklist: %s" % (channel, nick)
            else:
                y = y + ", " + nick
        return y

    def close(self):
        self.running = False
        self.connection.quit(self.settings.get("quitmsg", "Using DiscordIRCBot"))

    def set_running(self, value):
        self.running = False

    def on_featurelist(self, connection, event):
        global network
        featlen = len(event.arguments)
        for i in range(featlen):
            ce = event.arguments[i]
            spl = ce.split("=")
            if spl[0] == "NETWORK":
                network = spl[1]

    def on_whoreply(self, connection, event):
        global channelwho
        nick = event.arguments[4]
        host = event.arguments[2]
        channelwho.append([nick, host])

    def updatechanwho(self, target, host):
        global channelwho
        if host == "no":
            for pair in channelwho:
                nick = pair[0]
                if nick == target:
                    actualhost = pair[1]
                    channelwho.remove([target, actualhost])
                    return
        channelwho.append([target, host])

    def LtoS(self, s):
        string = " "
        return (string.join(s))

    def on_nicknameinuse(self, connection, event):
        connection.nick(connection.get_nickname() + "_")

    def identify(self):
        identify = self.settings["identify"]
        if identify == "True":
            try:
                self.NickServName = self.settings["NickServName"]
                self.NickServAcc = self.settings["NickServAcc"]
            except:
                self.NickServName = "NickServ"
                self.NickServAcc = self.settings["nickname"]
            self.NickServPass = self.settings["NickServPass"]
            self.NickServMsg = "identify " + self.NickServAcc + " " + self.NickServPass
            self.connection.privmsg(self.NickServName, self.NickServMsg)

    def on_welcome(self, connection, event):
        global channel
        global ignores
        self.identify()
        self.discord.loadtags()
        self.connection = connection
        channel = self.settings["channel"]
        ignores = self.settings["ignores"].split()
        time.sleep(2)
        connection.join(channel)
        with self.thread_lock:
            print("[IRC] Connected to server")

    def on_part(self, connection, event):
        if event.source.nick != connection.get_nickname():
            if len(event.arguments) == 0:
                extras = ""
            else:
                extras = event.arguments[0]
            info = {"source": "irc", "event": "part", "nick": event.source.nick, "time": int(time.time()), "extras": extras, "channel": channel}
            identhost = self.fromhost(event.source, "identhost")
            self.updatechanwho(event.source.nick, "no")
            message = "**{:s} just left {:s}**".format(\
                re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), channel)
            self.discord.send_my_message(message)

    def on_quit(self, connection, event):
        if event.source.nick != connection.get_nickname():
            self.updatechanwho(event.source.nick, "no")
            message = "**{:s} just quit {:s}**".format(\
                re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), network)
            self.discord.send_my_message(message)

    def on_kick(self, connection, event):
        nick = event.source.nick
        knick = str(event.arguments[0]).strip("'[]")
        self.updatechanwho(knick, "no")
        extras = str(event.arguments[1:]).strip("'[]")
        self.discord.send_my_message(nick + " kicked " + knick  + " (" + extras + " )")
        if event.arguments[0] == connection.get_nickname():
            self.connection.privmsg("Chanserv", "unban " + channel)
            time.sleep(2)
            connection.join(channel)

    def on_join(self, connection, event):
        if event.source.nick == connection.get_nickname():
            with self.thread_lock:
                print("[IRC] Joined " + channel)
            self.connection.who(channel)
            self.connection.privmsg(channel, "DiscIRC is now up and running!")
            self.discord.send_my_message("**DiscIRC is now up and running!**")
        if event.source.nick != connection.get_nickname():
            self.updatechanwho(event.source.nick, event.source.host)
            message = "**{:s} just joined {:s}**".format(\
                re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), channel)
            self.discord.send_my_message(message)

    def on_nick(self, connection, event):
        event_msg = "**" + event.source.nick + "** " + "is now known as" + " **" + event.target + "**"
        self.discord.send_my_message(event_msg)
        self.updatechanwho(event.source.nick, "no")
        self.updatechanwho(event.target, event.source.host)

    def stripcolors(self, m):
        m = m.replace("\x02", "")
        m = m.replace("\x0f", "")
        m = m.replace(chr(31), "")
        m = m.replace(chr(29), "")
        regexc = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
        m = regexc.sub("", m)
        return m

    def on_pubmsg(self, connection, event):
        isweather = []
        for nick in ignores:
            if nick == event.source.nick:
                print("Ignoring " + nick + ". Found in ignore list")
                return
        message = event.arguments[0].strip()
        message = "<**{:s}**> {:s}".format(\
            re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), message)
        regexc = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
        message = regexc.sub("", message)
        with self.thread_lock:
            print("[IRC] " + message)
        msg = event.arguments[0]
        msg = self.stripcolors(msg)
        msg = msg.split()
        isword = word.caller(event.source.nick, msg)
        if isword[0] == "success":
            self.sendtoboth(isword[1])
        elif isword[0] == "error":
            self.sendtoboth("Error: " + isword[1])
        isweather = weather.caller(msg, [event.source.nick, event.source.host])
        if isweather[0] == "error":
            wreply = "Error: " + isweather[1]
            self.sendtoboth(wreply)
        elif isweather[0] == "success":
            self.sendtoboth(isweather[1])
        if event.source.nick == self.settings["botowner"]:
            if event.arguments[0].strip() == "!cutrelay":
                self.discord.send_my_message("Discord Bot Shutting Down")
                time.sleep(2)
                self.discord.close()
                return
            if event.arguments[0].strip() == "!test":
                self.connection.privmsg(channel, chr(29) + "Hello world!")
                return
        self.discord.send_my_message(message)

    def on_action(self, connection, event):
        message = event.arguments[0].strip()
        message = "_* {:s} {:s}_".format(\
            re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), message)

        with self.thread_lock:
            print("[IRC] " + message)


        self.discord.send_my_message(message)
    def run(self):
        self.start()

        if self.running:
            self.running = False
            ircc = IRC({"irc": self.settings})
            ircc.set_discord(self.discord)
            self.discord.set_irc(ircc)
            ircc.set_thread_lock(self.thread_lock)
            ircc.run()
            ircc.run()
