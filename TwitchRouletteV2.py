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
    oldWeight = 0
    for user in online['streams']:
            name = user['channel']['name']
            game = user['game']
            viewers = user['viewers']
            newWeight =0

            for i in range(0,len(biasJSON['streams'])):
                if(name in biasJSON['streams'][i]['name']):
                    newWeight += int(biasJSON['streams'][i]['weight'])
            for i in range(0,len(biasJSON['games'])):
                #print(i, game)
                if(game in biasJSON['games'][i]['name']):
                    newWeight+=int(biasJSON['games'][i]['weight'])
                    #print(int(biasJSON['games'][i]['weight']))
                newWeight+=(viewers/V)

            if(newWeight>=oldWeight):
                topName = name
                oldWeight = newWeight
                #print(name,game,viewers,newWeight)
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
            startChat = "java -jar ./Chatty_0.8.1/Chatty.jar -channel {} -connect"
        streamThread = programThread(0,"Stream",startStream.format(stream))
        chatThread = programThread(1,"Chat", startChat.format(stream))

start()
streamThread.start()
chatThread.start()
streamThread.join()
