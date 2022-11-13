#################################################################################
#                                                                               #
# TODO: Get auth                                                                #
# TODO: Use command line inputs, then perhaps bash script                       #
# TODO: Try rewriting logging function                                          #
# TODO: Use different params for getrecenttracks (maybe)                        #
# TODO: Use try catch pls
#                                                                               #
#################################################################################

import json
import requests
import logging

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

GET_RECENT_TRACKS_URL = "%s?method=user.getrecenttracks&user=%s&api_key=%s&format=json" % (LAST_FM_API_BASE, USER_TO_LISTEN, LAST_FM_API_KEY)

def recLog(s, tabs):



def log(s):
    logger.debug(s)


def main():
    resp = requests.get(GET_RECENT_TRACKS_URL)
    respCode = resp.status_code

    # Just some error handling
    if respCode != 200:
        log("Bad response")
        exit()
    # Logging for debugging purposes
    log("Status code for GET_RECENT_TRACKS %s" % (str(respCode)))
    respContent = resp.json()
    log(respContent)
    latestTrack = respContent["recenttracks"]["track"][0] 
    isPlaying = respContent["recenttracks"]["track"][0]["@attr"]["nowplaying"]
    if isPlaying == "true":
        print("%s is currently listening to %s by %s" % (USER_TO_LISTEN, latestTrack["name"], latestTrack["artist"]["#text"]))
    else:
        print("%s is not currently listening to anything" % USER_TO_LISTEN)

main()
