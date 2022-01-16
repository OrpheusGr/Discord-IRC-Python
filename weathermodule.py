import requests
import json
import datetime
import csv
import os

global apikeys
global apikey
global LocationCache
LocationCache = []

f = open("settings.json", encoding="utf-8")
settings = json.loads(f.read())
f.close()
misc = settings["misc"]
apikeys = misc["weatherapikeys"].split()
apikey = apikeys[0]
global retries
retries = 0
checkfiles = ["locationcache.txt", "weatherlist.txt"]
for file in checkfiles:
    if os.path.isfile(file) == False:
        open(file, 'w').close()


def nextkey():
    global apikey
    ckey = apikeys.index(apikey) + 1
    if len(apikeys) <= ckey:
        nkey = apikeys[0]
    else:
        nkey = apikeys[ckey]
    return nkey

def LtoS(s):
    string = " "
    return (string.join(s))

def caller(msg, nickhost):
    if msg == []:
        return ["False"]
    symbol = msg[0][0]
    symbols = ["+", "!"]
    if symbol not in symbols:
        return ["False"]
    triggerw = ["weather", "w", "forecast", "f", "setweather"]
    triggerf = ["forecast", "f"]
    forecast = "no"
    wreply = ""
    cmd = msg[0][1:]
    if cmd == "setweather":
        if len(msg) < 2:
            return ["error", "You didn't provide a location to search for. Usage: setweather <location>"]
        query = LtoS(msg[1:])
        wreply = SetWeather(query, nickhost[0], nickhost[1])
        return wreply
    if cmd not in triggerw and cmd not in triggerf:
        return ["False"]
    if cmd in triggerf:
        forecast = "y"
    if len(msg) > 1:
        query = LtoS(msg[1:])
        loc = GetLocId(query)
        if loc[0] == "error":
            return loc
    else:
        loc = GetConfig(nickhost)
        if loc[0] == "_No_Location_Found_":
            return ["error", "No preset location found, set one with +setweather <location>"]
    if forecast == "y":
        wreply = GetForecast(loc[0], loc[1])
    else:
        wreply = GetWeather(loc[0], loc[1])
    return wreply

def GetConfig(nickhost):
    global weatherlist
    nickfound = 0
    hostfound = 0
    location = "_No_Location_Found_"
    locname = " "
    nlocation = location
    nlocname = " "
    nick = nickhost[0]
    host = nickhost[1]
    for i in weatherlist:
        if i[0] == host:
            hostfound = 1
            location = i[1]
            locname = i[2]
        if i[0] == nick:
            nickfound = 1
            nlocation = i[1]
            nlocname = i[2]
    if hostfound == 0:
        if nickfound:
            location = nlocation
            locname = nlocname
    return [location, locname]

def GetLocId(query):
    global retries
    global apikey
    data = {"apikey": apikey, "q": query, "language": "en", "details": "false", "offset": 1}
    r = requests.get("http://dataservice.accuweather.com/locations/v1/search", params=data)
    load = json.loads(r.text)
    if type(load) != list:
        iserror = load["Code"]
        if iserror == "ServiceUnavailable":
            while iserror == "ServiceUnavailable":
                retries += 1
                if retries == len(apikeys):
                    retries = 0
                    return ["error", "No working API keys at the moment."]
                print("WeatherMod Log: " + apikey + " Limit reached, looking for other key")
                apikey = nextkey()
                data = data = {"apikey": apikey, "q": query, "language": "en", "details": "false", "offset": 1}
                r = requests.get("http://dataservice.accuweather.com/locations/v1/search", params=data)
                load = json.loads(r.text)
                if type(load) != list:
                    iserror = load["Code"]
                else:
                    iserror = "no"
        else:
            return ["error", load["Message"]]
    if load == []:
        return ["error", "No results for the location you searched for"]
    load = load[0]
    if "Key" not in load:
        return ["error", "Unknown error occured while searching for your query."]
    loc = load["Key"]
    locname = load["EnglishName"] + ", " + load["Country"]["EnglishName"]
    locinfo = [loc, locname]
    LocInCache = AddToCache([query, loc, locname])
    if LocInCache[0]  == "True":
        return LocInCache[1]
    return locinfo

def AddToCache(queryloc):
    global LocationCache
    if queryloc not in LocationCache:
        LocationCache.append(queryloc)
        updateCache()
        return ["False", "No"]
    else:
        return ["True", [queryloc[1], queryloc[2]]]

def SetWeather(query, nick, hostorid):
    findkey = GetLocId(query)
    if findkey[0] == "error":
        return findkey
    else:
        adduserw(nick, hostorid, findkey[0], findkey[1])
        return ["success", "Your prefered location has been saved successfuly :)"]

def wcolor(t, u):
    c = "3"
    if u == "f":
        t = (t - 30) / 2
    st = str(t)
    if t <= -20:
        c = "15"
    if t < 0 and t >= -10:
        c = "11"
    if t > 0 and t <= 15:
        c = "10"
    if t > 15 and t <= 20:
        c = "12"
    if t > 20 and t < 27:
        c = "8"
    if t >= 27 and t <= 35:
        c = "7"
    if t > 35 and t <= 40:
        c = "4"
    if t > 40:
        c = "4\x02"

    return "\x03" + c + st + "\x0f"

def GetWeather(location, locname):
    global apikey
    global retries
    fullWeather = ""
    iserror = ""
    data = {"apikey": apikey, "language": "en", "details": "true"}
    url = "http://dataservice.accuweather.com/currentconditions/v1/%s" % (location)
    r = requests.get(url, params=data)
    load = json.loads(r.text)
    if type(load) != list:
        iserror = load["Code"]
        if iserror == "ServiceUnavailable":
            while iserror == "ServiceUnavailable":
                retries += 1
                if retries == len(apikeys):
                    retries = 0
                    return ["error", "No working API key"]
                print("WeatherMod Log:" + apikey + " Limit reached, looking for other key")
                apikey = nextkey()
                data = {"apikey": apikey, "language": "en", "details": "true"}
                url = "http://dataservice.accuweather.com/currentconditions/v1/%s" % (location)
                r = requests.get(url, params=data)
                load = json.loads(r.text)
                if type(load) != list:
                    iserror = load["Code"]
                else:
                    iserror = "no"
        else:
            return ["error", load["Message"]]
    if load == []:
        return ["error", "No results for the location you searched for"]
    load = load[0]
    condition = load["WeatherText"]
    dayornight = load["IsDayTime"]
    temp = load["Temperature"]
    Metric = temp["Metric"]
    Imperial = temp["Imperial"]
    MetricTemp = wcolor(Metric["Value"], "c")
    ImperialTemp = wcolor(Imperial["Value"], "f")
    MetricUnit = Metric["Unit"]
    ImperialUnit = Imperial["Unit"]
    Real = load["RealFeelTemperature"]
    RealMetric = Real["Metric"]
    RealImperial = Real["Imperial"]
    RealMetricTemp = wcolor(RealMetric["Value"], "c")
    RealImperialTemp = wcolor(RealImperial["Value"], "f")
    RealMetricUnit = RealMetric["Unit"]
    RealImperialUnit = RealImperial["Unit"]
    RealPhrase = RealMetric["Phrase"]
    Humidity = str(load["RelativeHumidity"]) + "%"
    Wind = load["Wind"]
    WindDir = Wind["Direction"]
    WindDeg = str(WindDir["Degrees"]) + "°"
    WindEng = WindDir["English"]
    WindSpeed = Wind["Speed"]
    WindSpeedMetric = WindSpeed["Metric"]["Value"]
    WindSpeedImperial = WindSpeed["Imperial"]["Value"]
    WindMetrUnit = "kph"
    WindImpUnit = "mph"
    Gust = load["WindGust"]["Speed"]
    GustMetric = Gust["Metric"]
    GustImperial = Gust["Imperial"]
    GustMetricSpeed = GustMetric["Value"]
    GustImperialSpeed = GustImperial["Value"]
    GustMetricUnit = "kph"
    GustImperialUnit = "mph"
    UVIndex = load["UVIndex"]
    UVText = load["UVIndexText"]
    Visibility = load["Visibility"]
    VisibMetric = Visibility["Metric"]["Value"]
    VisibImperial = Visibility["Imperial"]["Value"]
    VisibMetrUnit = Visibility["Metric"]["Unit"]
    VisibImpUnit = Visibility["Imperial"]["Unit"]
    CloudCover = load["CloudCover"]
    PressureMetric = load["Pressure"]["Metric"]["Value"]
    PressureImperial = load["Pressure"]["Imperial"]["Value"]
    PressUnitM = load["Pressure"]["Metric"]["Unit"]
    PressUnitI = load["Pressure"]["Imperial"]["Unit"]
    fullWeather = "[bold]Condition:[bold] %s %s%s %s%s | [bold]RealFeel:[bold] %s%s %s%s %s | [bold]Humidity:[bold] %s | [bold]Wind:[bold] %s%s/%s%s %s %s [bold]Gust:[bold] %s%s/%s%s | [bold]UV:[bold] %s %s | [bold]Visibility:[bold] %s%s %s%s | [bold]CloudCover:[bold] %s | [bold]Pressure:[bold] %s%s %s%s" % (condition, MetricTemp, MetricUnit, ImperialTemp, ImperialUnit, RealMetricTemp, RealMetricUnit, RealImperialTemp, RealImperialUnit, RealPhrase, Humidity, WindSpeedMetric, WindMetrUnit, WindSpeedImperial, WindImpUnit, WindDeg, WindEng, GustMetricSpeed, GustMetricUnit, GustImperialSpeed, GustImperialUnit, UVIndex, UVText, VisibMetric, VisibMetrUnit,VisibImperial, VisibImpUnit, CloudCover, PressureMetric, PressUnitM, PressureImperial, PressUnitI)
    fullWeather = locname + " " + fullWeather
    return ["success", fullWeather]

def GetForecast(location, locname):
    global apikey
    global retries
    theday = ""
    alldays = ""
    url = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/%s" % (location)
    data = {"apikey": apikey, "language": "en", "details": "true", "metric": "false"}
    r = requests.get(url, params=data)
    load = json.loads(r.text)
    if load == []:
        return ["error", "No results for the location you searched for"]
    if type(load) != list and "Code" in load:
        iserror = load["Code"]
        if iserror == "ServiceUnavailable":
            print("WeatherMod Log:" + apikey + " Limit reached, looking for other key")
            while iserror == "ServiceUnavailable":
                retries += 1
                if retries == len(apikeys):
                    retries = 0
                    return ["error", "No working API key"]
                apikey = nextkey()
                data = {"apikey": apikey, "language": "en", "details": "true"}
                url = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/%s" % (location)
                r = requests.get(url, params=data)
                load = json.loads(r.text)
                if type(load) != list:
                    iserror = load["Code"]
                    print("WeatherMod Log:" + apikey + " Limit reached, looking for other key")
                else:
                    iserror = "no"
        else:
            return ["error", load["Message"]]
    DF = load["DailyForecasts"]
    week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    xdate = datetime.datetime.now()
    today = xdate.strftime("%a")
    findtoday = week.index(today) - 1
    lastfcond = ""
    for day in DF:
        findtoday += 1
        todayis = week[findtoday]
        Temp = day["Temperature"]
        TempMin = Temp["Minimum"]
        TempMax = Temp["Maximum"]
        TempMinImp = wcolor(TempMin["Value"], "f")
        TempMaxImp = wcolor(TempMax["Value"], "f")
        TempImpUnit = "F"
        TempMinMetr = (int(TempMinImp) - 32) * 5.0/9.0
        TempMinMetr = wcolor(round(TempMinMetr,1))
        TempMaxMetr = (int(TempMaxImp) - 32) * 5.0/9.0
        TempMaxMetr = wcolor(round(TempMaxMetr,1))
        TempMetrUnit = "C"
        Air = day["AirAndPollen"][0]
        AirQValue = Air["Value"]
        AirQDesc = Air["Category"]
        AirQType = Air["Type"]
        Fcond = day["Day"]["ShortPhrase"]
        if Fcond == lastfcond:
            theday = "[bold][%s][bold] | %s-%s%s %s-%s%s | [bold]AQI:[bold] %s" % (todayis, TempMinMetr, TempMaxMetr, TempMetrUnit, TempMinImp, TempMaxImp, TempImpUnit, AirQDesc)
        else:
            theday = "[bold][%s][bold] %s | %s-%s%s %s-%s%s | [bold]AQI:[bold] %s" % (todayis, Fcond, TempMinMetr, TempMaxMetr, TempMetrUnit, TempMinImp, TempMaxImp, TempImpUnit, AirQDesc)
        lastfcond = Fcond
        alldays = alldays + " [bold]||[bold] " +  theday
        theday = ""
    alldays = locname + " " + alldays
    return ["success", alldays]

def loadweatherlist():
    global LocationCache
    global weatherlist
    weatherlist = []
    with open("weatherlist.txt", mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        for row in csv_reader:
            if len(row):
                user = row[0]
                utag = row[1]
                loc = row[2]
                weatherlist.append([user, utag, loc])
    with open("locationcache.txt", mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='|')
        for row in csv_reader:
            if len(row):
                LocationCache.append(row[0:])


def updateweatherlist(weatherlist):
    open("weatherlist.txt", 'w').close()
    with open('weatherlist.txt', mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for pair in weatherlist:
            csv_writer.writerow(pair)

def updateCache():
    global LocationCache
    open("locationcache.txt", 'w').close()
    with open('locationcache.txt', mode='a') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for pair in LocationCache:
            csv_writer.writerow(pair)

def adduserw(nick, hostorid, key, loc):
    global weatherlist
    weatherdel = []
    newweatherlist = []
    if len(weatherlist) == 0:
        weatherlist.append([hostorid, key, loc])
        weatherlist.append([nick, key, loc])
        updateweatherlist(weatherlist)
        return
    else:
        for pair in weatherlist:
            item = pair[0]
            data = pair[1]
            if item == nick or item == hostorid:
                weatherdel.append(pair)
        for pair in weatherlist:
            if pair not in weatherdel:
                newweatherlist.append(pair)
        newweatherlist.append([hostorid, key, loc])
        newweatherlist.append([nick, key, loc])
        weatherlist = newweatherlist
        updateweatherlist(newweatherlist)


loadweatherlist()
print("WeatherMod Log: Loaded weather list")
