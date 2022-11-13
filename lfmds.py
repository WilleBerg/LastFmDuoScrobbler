#################################################################################
#                                                                               #
# TODO: Get auth                                                                #
# TODO: Use command line inputs, then perhaps bash script                       #
# TODO: Try rewriting logging function                                          #
# TODO: Use different params for getrecenttracks (maybe)                        #
# TODO: Use try catch pls                                                       #  
# TODO: Save user's session key to file (if usable still)                       #
#                                                                               #
#################################################################################

import json
import webbrowser
import requests
import logging
import hashlib

# Create and configure logger
logging.basicConfig(filename="lfmdsLog.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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


def testing():
    token = getToken()
    print(token)
    getUserPermission(token)
    sessionKey = getSessionKey(token)


testing()

def main():
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

    latestTrack = respContent["recenttracks"]["track"][0] 
    try:
        isPlaying = respContent["recenttracks"]["track"][0]["@attr"]["nowplaying"]
    except KeyError as e:
        log("Could not find nowplaying")
        log("%s is probably not currently listening" % USER_TO_LISTEN)
        log(e)
        exit()

    if isPlaying == "true":
        print("%s is currently listening to %s by %s" % (USER_TO_LISTEN, latestTrack["name"], latestTrack["artist"]["#text"]))
    else:
        print("%s is not currently listening to anything" % USER_TO_LISTEN)

    getToken()

#main()
