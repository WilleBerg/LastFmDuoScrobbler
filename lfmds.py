#
# TODO: Get auth
# TODO: Find correct api
# 

import json

LAST_FM_API_KEY = "hej lol" #Get from config.json, but first get a key 
LAST_FM_API_BASE = "http://ws.audioscrobbler.com/2.0/"

GET_RECENT_TRACKS_URL = "%s?method=user.getrecenttracks&user=rj&api_key=%s&format=json" % (LAST_FM_API_BASE, LAST_FM_API_KEY)

def main():
    pass

main()
