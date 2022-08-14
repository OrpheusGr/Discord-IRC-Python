import irc.bot
import ssl
import re
import time
import weathermodule
weather = weathermodule
import wordcounter
word = wordcounter
import karmamodule
karma = karmamodule

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
    global channelwho
    channelwho = {}
    global warnlist
    warnlist = []
    global channelsetsopp
    def __init__(self, settings):
        irc.client.ServerConnection.buffer_class.encoding = "UTF-8"
        irc.client.ServerConnection.buffer_class.errors = "replace"
        ssl_factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        self.settings = settings["irc"]
        self.channelsets = settings["channelsets"]
        self.channelsetsopp = {}
        for c in self.channelsets:
            nc = self.channelsets[c].lower()
            self.channelsetsopp[nc] = c
            self.channelsets[c] = self.channelsets[c].lower()
        ssl_kwargs = {"connect_factory": ssl_factory}
        if self.settings["ssl"] == "True":
            irc.bot.SingleServerIRCBot.__init__(self, [\
                (settings["irc"]["server"],\
                int(settings["irc"]["port"]))],\
                settings["irc"]["nickname"],\
                settings["irc"]["nickname"],
                **ssl_kwargs)
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [\
                (settings["irc"]["server"],\
                int(settings["irc"]["port"]))],\
                settings["irc"]["nickname"],\
                settings["irc"]["nickname"])


    def set_discord(self, discordc):
        self.discord = discordc

    def roll_back(self, msg, left, right):
        while right > 0 and msg[left + right] != ' ':
            right -= 1
        return right

    def split_msg(self, msg, channel):
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

    def sendtoboth(self, message, ircchan, discordchan):
        self.send_my_message(message.replace("[bold]", "\x02"), ircchan)
        self.discord.send_my_message(self.stripcolors(message.replace("[bold]", "**")), discordchan)

    def send_my_message(self, message, channel):
        message = message.replace("[bold]", "\x02")
        if len(message) >= 480:
            self.split_msg(message, channel)
        else:
            self.connection.privmsg(channel, message.strip())

    def warnkickban(self, message, nick, channel):
        global warnlist
        warnexcept = self.settings["warnexcept"].split()
        if nick.lower() in warnexcept:
            return
        warns = 0
        message = message.lower()
        message = message.split()
        badwords = self.settings["badwords"].split()
        for word in message:
            if word.lower() in badwords:
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
                            self.kicknick(nick, kreason, 0, channel)
                            warnlist.remove(pair)
                            warns += 1
                            warnlist.append([nick, warns])
                        elif warns == 3:
                            kreason = "You have been warned about using such terms in here. Goodbye."
                            self.kicknick(nick, kreason, 1, channel)
                            warnlist.remove(pair)
                            return
                if warns == 0:
                    addwarn = [nick, 1]
                    warnlist.append(addwarn)
                    self.send_my_message(nick + ": Please avoid using such terms in " + channel + ". Excessive use will lead into a ban. Respect everyone :)", channel)
                    return

    def fromhost(self, host, part):
        if iswm.match("*!*@*", host) == False:
            return None
        if part == "ident":
            return host.split("!").split("@")[0]
        if part == "identhost":
            return host.split("!")[1]
        else:
            return host


    def kicknick(self, knick, kreason, ban, channel):
        chanservkick = self.settings["chanservkick"]
        isnick = self.isonchan(knick, channel)
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

    def isonchan(self, target, channel):
        global channelwho
        currchan = channelwho[channel]
        for pair in currchan:
            nick = pair[0].lower()
            if nick == target.lower():
                return "True"
        return "False"

    def gethost(self, user):
        global channelwho
        for chan in channelwho:
            loopchan = channelwho[chan]
            for pair in loopchan:
                nick = pair[0]
                if nick == user:
                    host = pair[1]
                    return host
            return "False"

    def nicklist(self, channel):
        if self.settings["send_nick_list"] == "False":
            return "Command disabled."
        global channelwho
        currchan = channelwho[channel]
        y = ""
        for pair in currchan:
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
        channel = event.arguments[0].lower()
        nick = event.arguments[4]
        host = event.arguments[2]
        if channel not in channelwho:
            channelwho[channel] = []
        channelwho[channel].append([nick, host])

    def updatechanwho(self, target, host, channel):
        global channelwho
        if channel not in channelwho:
            return
        currchan = channelwho[channel]
        if host == "no":
            for pair in currchan:
                nick = pair[0]
                if nick == target:
                    actualhost = pair[1]
                    currchan.remove(pair)
                    return
        currchan.append([target, host])

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
        global ignores
        self.identify()
        self.discord.loadtags()
        self.discord.setstatus()
        self.connection = connection
        ignores = self.settings["ignores"].split()
        time.sleep(2)
        chanl = self.channelsets
        for c in chanl:
            connection.join(chanl[c])
        with self.thread_lock:
            print("[IRC] Connected to server")

    def on_part(self, connection, event):
        nick = event.source.nick
        ircchan = event.target.lower()
        discordchan = self.discord.toch(self.channelsetsopp[ircchan])
        if nick != connection.get_nickname():
            self.updatechanwho(nick, "no", ircchan)
            try:
                reason = "(" + event.arguments[0] + ")"
            except IndexError:
                reason = ""
            message = "<- **%s just left %s %s**" % (nick, ircchan, reason)
            self.discord.send_my_message(message, discordchan)


    def on_quit(self, connection, event):
        nick = event.source.nick
        if nick != connection.get_nickname():
            try:
                reason = event.arguments[0]
            except:
                reason = ""
            message = "<- **%s just quit %s (%s)**" % (nick, network, reason)
            for ch in channelwho:
                currchan = channelwho[ch]
                for pair in currchan:
                    if nick == pair[0]:
                        self.updatechanwho(nick, "no", ch)
                        discordchan = self.discord.toch(self.channelsetsopp[ch])
                        self.discord.send_my_message(message, discordchan)

    def on_kick(self, connection, event):
        nick = event.source.nick
        knick = event.arguments[0]
        channel = event.target.lower()
        discordchan = self.discord.toch(self.channelsetsopp[channel])
        self.updatechanwho(knick, "no", channel)
        try:
            extras = "(" + event.arguments[1] + ")"
        except IndexError:
            extras = ""
        self.discord.send_my_message("**%s kicked %s %s**" % (nick, knick, extras), discordchan)
        if knick == connection.get_nickname():
            self.connection.privmsg("Chanserv", "unban " + channel)
            time.sleep(2)
            connection.join(channel)

    def on_join(self, connection, event):
        nick = event.source.nick
        channel = event.target.lower()
        discordchan = self.discord.toch(self.channelsetsopp[channel])
        if nick == connection.get_nickname():
            with self.thread_lock:
                print("[IRC] Joined " + channel)
            self.connection.who(channel)
            self.discord.send_my_message("**DiscIRC is now up and running!**", discordchan)
        else:
            self.updatechanwho(nick, event.source.host, channel)
            message = "-> **%s just joined %s**" %  (nick, channel)
            self.discord.send_my_message(message, discordchan)

    def on_nick(self, connection, event):
        nick = event.source.nick
        host = event.source.host
        newnick = event.target
        event_msg = "**%s** *is now known as* **%s**" % (nick, newnick)
        for ch in channelwho:
            currchan = channelwho[ch]
            for pair in currchan:
                if nick == pair[0]:
                    discordchan = self.discord.toch(self.channelsetsopp[ch])
                    self.discord.send_my_message(event_msg, discordchan)
                    self.updatechanwho(event.source.nick, "no", ch)
                    self.updatechanwho(newnick, event.source.host, ch)

    def stripcolors(self, m):
        m = m.replace("\x02", "")
        m = m.replace("\x0f", "")
        m = m.replace(chr(31), "")
        m = m.replace(chr(29), "")
        regexc = re.compile("\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
        m = regexc.sub("", m)
        return m

    def on_pubmsg(self, connection, event):
        channel = event.target.lower()
        discordchan = self.discord.toch(self.channelsetsopp[channel])
        isweather = []
        for nick in ignores:
            if nick == event.source.nick:
                print("Ignoring " + nick + ". Found in ignore list")
                return
        msg = event.arguments[0]
        msg = self.stripcolors(msg)
        msg = msg.split()
        msg_string = self.LtoS(msg)
        sender = event.source.nick
        message = "<**%s**> %s" % (sender, msg_string)
        self.discord.send_my_message(message, discordchan)
        self.warnkickban(msg_string, sender, channel)
        with self.thread_lock:
            print("[IRC] <%s> %s" % (sender, msg_string))
        if msg[0] ==  "!disclist":
            self.discord.send_list(channel)
        iskarma = karma.caller(msg, sender)
        if iskarma:
            self.sendtoboth(iskarma, channel, discordchan)
        isword = word.caller(sender, msg)
        if isword[0] == "success":
            self.sendtoboth(isword[1], channel, discordchan)
        elif isword[0] == "error":
            self.sendtoboth("Error: " + isword[1], channel, discordchan)
        isweather = weather.caller(msg, [sender, event.source.host])
        if isweather[0] == "error":
            wreply = "Error: " + isweather[1]
            self.sendtoboth(wreply, channel, discordchan)
        elif isweather[0] == "success":
            self.sendtoboth(isweather[1], channel, discordchan)
        if sender == self.settings["botowner"]:
            if msg[0] == "!cutrelay":
                self.discord.send_to_all("Discord Bot Shutting Down")
                time.sleep(2)
                self.discord.close()
                return

    def on_action(self, connection, event):
        message = event.arguments[0].strip()
        channel = event.target.lower()
        discordchan = self.discord.toch(self.channelsetsopp[channel])
        self.warnkickban(self.LtoS(event.arguments[0:]), event.source.nick, channel)
        message = "_* {:s} {:s} _".format(\
            re.sub(r"(]|-|\\|[`*_{}[()#+.!])", r'\\\1', event.source.nick), message)

        with self.thread_lock:
            print("[IRC] " + message)


        self.discord.send_my_message(message, discordchan)

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
