#################################################################################
#                                                                               #
# TODO: Use command line inputs, then perhaps bash script                       #
# TODO: Use different params for getrecenttracks (maybe)                        #
# TODO: Use try catch pls                                                       #  
# TODO: Save user's session key to file (if usable still)                       #
# TODO: Fix updateNowPlaying for when the same song is on repeat                #
# TODO: Maybe constantly send updateNowPlaying requests, or every other loop    #
#       iteration.                                                              #
#                                                                               #
#################################################################################

import json
import webbrowser
import requests
import logging
import hashlib
import time

# Create and configure logger
logging.basicConfig(filename="lfmdsLog.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

configObj = json.load(open('./config.json', 'r'))

# Fun api stuff
LAST_FM_API_KEY = configObj["apiKey"]  #Get from config.json, but first get a key 
LAST_FM_API_BASE = "http://ws.audioscrobbler.com/2.0/"

# The user which is currently listening to music/is scrobbling
USER_TO_LISTEN = configObj["userToListen"]

GET_RECENT_TRACKS_URL = "%s?method=user.getrecenttracks&user=%s&api_key=%s&format=json&limit=5" % (LAST_FM_API_BASE, USER_TO_LISTEN, LAST_FM_API_KEY)

def recLog(s, tabs):
    if type(s) != dict and type(s) != list:
       logger.debug(tabs + str(s)) 
       return
    if type(s) == list:
        logger.debug(tabs + "[")
        for item in s:
            recLog(item, tabs + "    ")
        logger.debug(tabs + "]")
    if type(s) == dict:
        logger.debug(tabs + "{")
        for key, value in s.items():
            logger.debug(tabs + str(key) + " : ")
            recLog(value, tabs + "    ")
        logger.debug(tabs + "}")



def log(s):
    recLog(s, "")

def getTokenSignature():
    signatureString = "api_key" + LAST_FM_API_KEY + "methodauth.getToken" + configObj["secret"]
    md5String = hashlib.md5(signatureString.encode('utf-8')).hexdigest()
    return md5String
    

def getToken():
    signature = getTokenSignature()
    url = "%s?method=auth.getToken&api_key=%s&api_sig=%s&format=json" % (LAST_FM_API_BASE, LAST_FM_API_KEY, signature)
    resp = requests.get(url)
    try:
        respContent = resp.json()
        log(respContent)
    except:
        log("Could not get token")
    return respContent["token"]

def getUserPermission(token):
    url = "http://www.last.fm/api/auth/?api_key=%s&token=%s" % (LAST_FM_API_KEY, token)
    webbrowser.open(url, new = 0, autoraise = True)
    print("Please allow access to your account")
    while True:
        try:
            input("Press enter when you have allowed access")
            break
        except:
            pass
    

def getSessionKey(token):
    auth_sig = "api_key" + LAST_FM_API_KEY + "methodauth.getSessiontoken" + token + configObj["secret"]
    md5String = hashlib.md5(auth_sig.encode('utf-8')).hexdigest()
    url = "%s?method=auth.getSession&api_key=%s&token=%s&format=json&api_sig=%s" % (LAST_FM_API_BASE, LAST_FM_API_KEY, token, md5String)
    resp = requests.get(url)
    try:
        respContent = resp.json()
        log(respContent)
    except Exception as e:
        log(e)
    return respContent["session"]["key"] 


def scrobbleSong(songName, artistName, album, timestamp, sessionKey):
    auth_sig = "album" + album + "api_key" + LAST_FM_API_KEY + "artist" + artistName + "methodtrack.scrobblesk" + sessionKey + "timestamp" + timestamp + "track" + songName + configObj["secret"]
    md5String = hashlib.md5(auth_sig.encode('utf-8')).hexdigest()
    url = "%s?method=track.scrobble&api_key=%s&sk=%s&track=%s&artist=%s&album=%s&timestamp=%s&api_sig=%s&format=json" % (LAST_FM_API_BASE, LAST_FM_API_KEY, sessionKey, songName, artistName, album, timestamp, md5String)
    resp = requests.post(url)
    try:
        respContent = resp.json()
        log(respContent)
    except Exception as e:
        log(e)

def updateNowPlaying(songName, artistName, album, sessionKey):
    auth_sig = "album" + album + "api_key" + LAST_FM_API_KEY + "artist" + artistName + "methodtrack.updateNowPlaying" + "sk" + sessionKey + "track" + songName + configObj["secret"]
    md5String = hashlib.md5(auth_sig.encode('utf-8')).hexdigest()
    resp = requests.post("%s?method=track.updateNowPlaying&api_key=%s&sk=%s&track=%s&artist=%s&album=%s&api_sig=%s&format=json" % (LAST_FM_API_BASE, LAST_FM_API_KEY, sessionKey, songName, artistName, album, md5String))
    try:
        respContent = resp.json()
        log(respContent)
    except Exception as e:
        log(e)
    

def testing():
    token = getToken()
    print(token)
    getUserPermission(token)
    sessionKey = getSessionKey(token)
    print(sessionKey)



def main():

    currentlyPlayingProgram = {
        "name" : "",
        "artist" : "",
        "album" : "",
    }
    lastPlayedSongProgram = {
        "name" : "",
        "artist" : "",
        "album" : "",
        "timestamp" : ""
    }

    token = getToken()
    #getUserPermission(token)
    sessionKey = configObj["sessionKey"] #getSessionKey(token) 

    resp = requests.get(GET_RECENT_TRACKS_URL)
    respCode = resp.status_code

    # Just some error handling
    if respCode != 200:
        log("Bad response")
        exit()
    # Logging for debugging purposes
    log("Status code for GET_RECENT_TRACKS %s" % (str(respCode)))
    try:
        respContent = resp.json()
    except Exception as e:
        log(e)

    log(respContent)

    latestTrackOnLastFm = respContent["recenttracks"]["track"][0] 
    try:
        isPlaying = respContent["recenttracks"]["track"][0]["@attr"]["nowplaying"]
    except KeyError as e:
        log("Could not find nowplaying")
        log("%s is probably not currently listening" % USER_TO_LISTEN)
        log(e)
        isPlaying = "false"

    

    timestamp = str(int(time.time()))

    if isPlaying == "true":
        currentlyPlayingProgram["name"] = latestTrackOnLastFm["name"]
        currentlyPlayingProgram["artist"] = latestTrackOnLastFm["artist"]["#text"]
        currentlyPlayingProgram["album"] = latestTrackOnLastFm["album"]["#text"]
    else:
        lastPlayedSongProgram["name"] = latestTrackOnLastFm["name"]
        lastPlayedSongProgram["artist"] = latestTrackOnLastFm["artist"]["#text"]
        lastPlayedSongProgram["album"] = latestTrackOnLastFm["album"]["#text"]
        lastPlayedSongProgram["timestamp"] = latestTrackOnLastFm["date"]["uts"]
        
    # Bad code i know
    while True:
        resp = requests.get(GET_RECENT_TRACKS_URL)
        respCode = resp.status_code

        # Just some error handling
        if respCode != 200:
            log("Bad response")
            log(resp.json())
            logger.critical("Bad response from get recent tracks")
            time.sleep(10)
            continue
        # Logging for debugging purposes
        log("Status code for GET_RECENT_TRACKS %s" % (str(respCode)))
        try:
            respContent = resp.json()
        except Exception as e:
            log(e)

        latestTrackOnLastFm = respContent["recenttracks"]["track"][0] 
        try:
            isPlaying = respContent["recenttracks"]["track"][0]["@attr"]["nowplaying"]
            log("Currently playing")
        except KeyError as e:
            log("Could not find nowplaying")
            log("%s is probably not currently listening" % USER_TO_LISTEN)
            log(e)
            isPlaying = "false"

        currentlyPlayingOnLastFm = {
            "name" : "",
            "artist" : "",
            "album" : "",
        }
        lastPlayedSongOnLastFm = {
            "name" : "",
            "artist" : "",
            "album" : "",
            "timestamp" : ""
        }

        log("Track 0")
        log(respContent["recenttracks"]["track"][0])
        log("Track 1")
        log(respContent["recenttracks"]["track"][1])

        log("Currently playing on program")
        log(currentlyPlayingProgram)
        log("Last played song on program")
        log(lastPlayedSongProgram)

        timestamp = str(int(time.time()))

        if isPlaying == "true":
            currentlyPlayingOnLastFm["name"] = latestTrackOnLastFm["name"]
            currentlyPlayingOnLastFm["artist"] = latestTrackOnLastFm["artist"]["#text"]
            currentlyPlayingOnLastFm["album"] = latestTrackOnLastFm["album"]["#text"]
            lastPlayedSongOnLastFm["name"] = respContent["recenttracks"]["track"][1]["name"]
            lastPlayedSongOnLastFm["artist"] = respContent["recenttracks"]["track"][1]["artist"]["#text"]
            lastPlayedSongOnLastFm["album"] = respContent["recenttracks"]["track"][1]["album"]["#text"]
            lastPlayedSongOnLastFm["timestamp"] = respContent["recenttracks"]["track"][1]["date"]["uts"]
            if currentlyPlayingProgram["name"] != currentlyPlayingOnLastFm["name"]: #temporary >:(
                updateNowPlaying(currentlyPlayingOnLastFm["name"], currentlyPlayingOnLastFm["artist"], currentlyPlayingOnLastFm["album"], sessionKey)
                currentlyPlayingProgram = currentlyPlayingOnLastFm
        else:
            lastPlayedSongOnLastFm["name"] = latestTrackOnLastFm["name"]
            lastPlayedSongOnLastFm["artist"] = latestTrackOnLastFm["artist"]["#text"]
            lastPlayedSongOnLastFm["album"] = latestTrackOnLastFm["album"]["#text"]
            lastPlayedSongOnLastFm["timestamp"] = latestTrackOnLastFm["date"]["uts"]

        if lastPlayedSongProgram != lastPlayedSongOnLastFm:
            if lastPlayedSongProgram["timestamp"] != lastPlayedSongOnLastFm["timestamp"]:
                scrobbleSong(lastPlayedSongOnLastFm["name"], lastPlayedSongOnLastFm["artist"], lastPlayedSongOnLastFm["album"], lastPlayedSongOnLastFm["timestamp"], sessionKey)
                lastPlayedSongProgram = lastPlayedSongOnLastFm

        time.sleep(1)



main()
