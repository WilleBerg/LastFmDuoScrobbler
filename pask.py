#Permission and session key script

import json
import webbrowser
import requests
import logging
import hashlib
import time

configObj = json.load(open('./config.json', 'r'))

LAST_FM_API_KEY = configObj["apiKey"]  #Get from config.json, but first get a key 
LAST_FM_API_BASE = "http://ws.audioscrobbler.com/2.0/"

###############################################################################
#                          LOGGING CONFIGURATION                              #
###############################################################################

logging.basicConfig(filename="paskLog.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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

###############################################################################
#                                  MAIN                                       #
###############################################################################

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

def main():
    token = getToken()
    getUserPermission(token)
    sessionKey = getSessionKey(token)
    configObj["sessionKey"] = sessionKey
    with open('./config.json', 'w') as outfile:
        json.dump(configObj, outfile)
    print("Session key saved to config.json")

main()
    
