import re
import pickle
import os
global delconfirm
delconfirm = {}
checkfiles = ["countdict.txt"]
for file in checkfiles:
    if os.path.isfile(file) == False:
        open(file, 'w').close()


def caller(nick, message):
    global countdict
    global delconfirm
    if message == []:
        return ["bleh"]
    m = message
    symbols = ["+", "!"]
    sym = m[0][0]
    triggers = ["wordlist", "listwords", "delword", "addword", "wordcount", "wcount"]
    cmd = m[0][1:]
    if cmd not in triggers:
        for key in countdict:
            x = m.count(key)
            if x:
                if nick not in countdict[key]:
                    countdict[key][nick] = 0
                y = countdict[key][nick]
                countdict[key][nick] = y + 1
        savecount(countdict)
        return ["successwordcheck"]
    word = LtoS(m[1:])
    if sym not in symbols:
        return ["bleh"]
    if cmd == "addword":
        if word == "":
            return ["error", "What word? You didn't provide one :o"]
        if word in countdict:
            return ["error", word + " is already in my list. Check its stats with wordcount " + word]
        if word not in countdict:
            countdict[word] = {"botdummydict": 0}
            savecount(countdict)
            return ["success", "Word added to countlist"]
        else:
            return ["error", "Word already in countlist"]
    elif cmd in ["wordcount", "wcount"]:
        if word in countdict:
            if countdict[word] == {}:
                return ["error", "No stats for this word yet."]
            sorted_w = sorted(countdict[word].items(), key=lambda x: x[1], reverse=True)
            finalsorted = ""
            for tup in sorted_w:
                if tup[0] != "botdummydict":
                    cpair = "\x02" + tup[0] + "\x02" +  ": " +  str(tup[1]) + " • "
                    finalsorted = finalsorted + cpair
            if finalsorted == "":
                return ["error", "No stats for this word yet."]
            return ["success", finalsorted]
        else:
            return ["error", "No such word in my list. Add it with addword"]
    elif cmd == "delword" or cmd == "remword":
        if word == "":
            return ["error", "What word? You didn't provide one!"]
        if word not in countdict and delconfirm == {}:
            return ["error", "No such word in my list."]
        if delconfirm == {}:
            delconfirm = {word: {nick: 1}}
            return ["success", "If you really want to delete this word resend the command."]
        if word not in delconfirm:
            delconfirm = {}
            return ["error", "Proccess broken...Please repeat the same command to delete a word."]
        if word in delconfirm:
            if nick in delconfirm[word]:
                delconfirm = {}
                del countdict[word]
                savecount(countdict)
                return ["success", word + " Stats deleted."]
    elif cmd == "wordlist" or cmd == "listwords":
        if countdict == {}:
            return ["error", "No words in my list yet! Add one with !addword"]
        wordlist = ""
        tcount = 0
        for keyw in countdict:
            for keykeyw in countdict[keyw]:
                tcount = tcount + countdict[keyw][keykeyw]
            wordlist = wordlist +  "\x02" + keyw + "\x02" + ": " +  str(tcount) + " • "
            tcount = 0
        return ["success", wordlist]

def LtoS(s):
    string = " "
    return (string.join(s))


def savecount(dict):
    with open("countdict.txt", "wb") as countwrite:
        pickle.dump(dict, countwrite)

def loadcount():
    global countdict
    try:
        with open("countdict.txt", "rb") as countread:
            countdict = pickle.loads(countread.read())
    except EOFError:
        countdict = {}
    print("WordCount Log: Stats loaded.")

loadcount()
