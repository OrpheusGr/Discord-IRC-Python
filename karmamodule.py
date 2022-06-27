import csv
import os

checkfiles = ["karma.txt"]
for file in checkfiles:
    if os.path.isfile(file) == False:
        open(file, 'w').close()


def caller(msg, nick):
    trigger = msg[0]
    if trigger == "+karma":
         if len(msg) == 1:
             query = nick
         elif len(msg) > 1:
             query = msg[1]
         for pair in karmalist:
             i = pair[0]
             a = pair[1]
             if i == query:
                 return "%s's karma is %s" % (i, a)
         return "%s's karma is 0" % (query)
    l = len(trigger)
    postfix = trigger[-2:]
    if postfix not in ["--", "++"]:
        return
    prel = l - 2
    prefix = trigger[0:prel]
    reply = changekarma(prefix, postfix, nick)
    return reply


def loadkarma():
    global karmalist
    karmalist = []
    with open("karma.txt", mode="r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if len(row):
                word = row[0]
                karma = int(row[1])
                karmalist.append([word, karma])


def updatekarma(karmalist):
    open("karma.txt", 'w').close()
    with open('karma.txt', mode='a') as karma:
        karmawriter = csv.writer(karma, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for pair in karmalist:
            karmawriter.writerow(pair)

def changekarma(prefix, postfix, nick):
    global karmalist
    newlist = []
    prefixfound = 0
    for pair in karmalist:
        pre = pair[0]
        amount = pair[1]
        if pre != prefix:
            newlist.append(pair)
        else:
            prefixfound = 1
            if postfix == "--":
                newamount = amount - 1
            if postfix == "++":
                newamount = amount + 1
            newlist.append([prefix, newamount])
    if prefixfound == 0:
        prefixfound = 1
        if postfix == "--":
            newamount = -1
            newlist.append([prefix, -1])
        if postfix == "++":
            newamount = 1
            newlist.append([prefix, 1])
    karmalist = newlist
    updatekarma(karmalist)
    reply = "%s's karma is now %s" % (prefix, newamount)
    return reply

loadkarma()
