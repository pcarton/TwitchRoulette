import os
import subprocess
import threading
import json
import urllib.request, urllib.error, urllib.parse
from numpy.random import choice
import sys
import locale
from settings import auth

e=locale.getdefaultlocale()[1]

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
blCasters = []
blGames = []
fileCasterBiases = []
fileGameBiases = []
listCasters = []
listBiases = []
listWeights = []

constantlyRunning = False

casterFile = open('CasterBiases.txt', 'r+')
for line in casterFile:
        fileCasterBiases.append(line.split('*',1))
casterFile.close()
#print fileCasterBiases

gameFile = open('GameBiases.txt','r+')
for line in gameFile:
        fileGameBiases.append(line.split('*',1))
gameFile.close()
#print fileGameBiases

blCasterFile = open('CasterBlacklist.txt', 'r+')
for line in blCasterFile:
        blCasters.append(line.strip())
blCasterFile.close()
#print blCasters

blGameFile = open('GameBlacklist.txt','r+')
for line in blGameFile:
        blGames.append(line.strip())
blGameFile.close()
#print blGames

def determineBias(name,game,viewers):
        cb = getCasterBias(name)
        gb = getGameBias(game)
        vb = getViewerBias(viewers)
        return cb+gb+vb

def getCasterBias(name):
        for x,y in fileCasterBiases:
                if x in name:
                        return float(y)

        return 1.0;
def getGameBias(game):
        for x,y in fileGameBiases:
                if game!=None and x in game:
                        return float(y)
        return 1.0;
def getViewerBias(viewers):
        viewers=int(viewers)
        if(viewers>2000):
                return 20.0
        elif(viewers>1000):
                return 10.0
        elif(viewers>500):
                return 5.0
        elif(viewers>300):
                return 3.0
        else:
                return 1.0

def biasToWeights():
        global listBiases
        global listWeights
        total = 0
        for x in listBiases:
                total+=x
        for y in listBiases:
                if y>=0:
                        listWeights.append(y/total)
                else:
                        listWeights.append(0)

def start():
        global listWeights
        global listCasters
        global listBiases
        global streamThread
        global chatThread
        global constantlyRunning

        listWeights = []
        listCasters = []
        listBiases = []

        versionRequest1 = urllib.request.Request("https://api.twitch.tv/kraken/streams/followed?limit=75", headers={"Accept" : "application/vnd.twitchtv.v3+json", "Authorization" : auth})
        #print(versionRequest1)
        streamsFromAPI =urllib.request.urlopen(versionRequest1).read().decode('ascii','ignore')
        #print(streamsFromAPI.replace('\\','\\\\'))
        #print(streamsFromAPI)
        streamsJSON = json.loads(streamsFromAPI)
        for user in streamsJSON['streams']:
                name = user['channel']['name']
                game = user['game']
                viewers = user['viewers']
                bias = determineBias(name,game,viewers)
                if not name in blCasters and not game in blGames:
                        listCasters.append(name)
                        listBiases.append(bias)
                        print(listCasters.index(name), name , game, viewers)
        biasToWeights()
        #print(listCasters)
        #print(listBiases)
        #print(listWeights)
        if not constantlyRunning:
                selection = input("Select Caster, q to quit, or r for random\n")
        else:
                selection = 'r'
        if selection == 'q':
                sys.exit()
        elif selection.find('c') != -1:
                constantlyRunning = True
                selection = selection.replace('c','')
        if selection == 'r' or int(selection)>= len(listCasters):
                stream = choice(listCasters, p=listWeights)
                print(stream + " chosen.")
        else:
                stream = listCasters[int(selection)]
                print(stream+" chosen.")

        startStream = "livestreamer twitch.tv/{} best"
        startChat = "javaw -jar .\\Chatty_0.8.1\\Chatty.jar -channel {} -connect"

        streamThread = programThread(0,"Stream",startStream.format(stream))
        chatThread = programThread(1,"Chat", startChat.format(stream))

start()
#while(true)
streamThread.start()
chatThread.start()
streamThread.join()
#start()
