import os
import subprocess
import threading
import json
import urllib.request, urllib.error, urllib.parse
import sys
import locale
from settings import auth

e=locale.getdefaultlocale()[1]
biasJSON = None
V = 1000

class programThread(threading.Thread):
        def __init__(self, threadID, name,arg):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.arg = arg

        def run(self):
                with open(os.devnull,'wb') as devnull:
                        subprocess.call(self.arg, stdout=devnull, shell=True)

        def stop(self):
                self.running = False


with open('biases.json', 'r+') as biasFile:
    biasJSON = json.load(biasFile)
biasFile.close()

def chooseStream(online):
    topName = ""
    topGame = ""
    topViewers = 0
    for user in online['streams']:
            name = user['channel']['name']
            game = user['game']
            viewers = user['viewers']
            newWeight =0

            if(name in biasJSON['streams']):
                newWeight += int(biasJSON['streams'][name]['weight'])
            if(game in biasJSON['games']):
                newWeight+=int(biasJSON['games'][game]['weight'])
            newWeight+=viewers/V
            if(topName in biasJSON['streams']):
                oldWeight = int(biasJSON['streams'][topName]['weight'])
            else:
                #print(name)
                oldWeight = 0
            if(topGame in biasJSON['games']):
                oldGame = int(biasJSON['games'][topGame]['weight'])
            else:
                #print(game)
                oldGame = 0
            oldViewers = topViewers/V
            oldWeight += oldGame
            oldWeight += oldViewers
            if(newWeight>=oldWeight):
                topName = name
                topGame = game
                topViewers = viewers
    return topName

def start():
        global streamThread
        global chatThread

        versionRequest1 = urllib.request.Request("https://api.twitch.tv/kraken/streams/followed?limit=75", headers={"Accept" : "application/vnd.twitchtv.v3+json", "Authorization" : auth})
        streamsFromAPI =urllib.request.urlopen(versionRequest1).read().decode('ascii','ignore')
        streamsJSON = json.loads(streamsFromAPI)


        stream = chooseStream(streamsJSON)
        startStream = "livestreamer twitch.tv/{} best"
        if(os.name!='posix'):
            startChat = "javaw -jar .\\Chatty_0.8.1\\Chatty.jar -channel {} -connect"
        else:
            startChat = "java -jar .\\Chatty_0.8.1\\Chatty.jar -channel {} -connect"
        streamThread = programThread(0,"Stream",startStream.format(stream))
        chatThread = programThread(1,"Chat", startChat.format(stream))

start()
streamThread.start()
chatThread.start()
streamThread.join()
