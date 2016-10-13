from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import Image
from kivy.config import Config
import webbrowser
import requests
import time
import html


#sets the window to not be resizeable, aswell as non-borderloss so you can still drag the window around
Config.set('graphics','resizable',0)
Config.set('graphics','borderless',0)

#disable the default kivy touch detection (rightclick normally leaves an orange dot)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.write()

#set window size
Window.size = (1000, 610)

#time interval for how often the script checks if it can update the title
global timeInterval
timeInterval = 10



class TitleUpdater(Widget):
    def init2(self):     
        #set variables to default values
        self.tempSettings2 = []
        self.scriptActive = False
        self.preText = ""
        self.postText = ""
        self.myIngameIDs = []
        self.twitchChannel = ""
        self.oauth = ""
        self.clientID = ""
        self.allowUpdateWhileInReplay = 1
        self.includeRaces = 1
        self.includeOpponentName = 1
        self.includeTimeStamp = 1
        self.lastPutString = ""

        self.creditText.text = "\n\n\n\n\n\n\n\nThanks to Blizzard and Twitch for making this possible via API\n\
        Thanks to Python, Kivy and PyInstaller for letting me turn this script into an .exe file\n\
        Thanks to my friends Pundurs, Zither, Propagare, Hymirth and Crexis for helping and testing\n\
        \n\
        Created by [GG]BuRny alias BurnySc2\n\
        2016"
    
    def update(self, dt):    
        global timeInterval

        #if the "script activated?" box isn't active, this function does nothing
        if not self.scriptActiveBox.active:
            return 0

        #update the variables from the text-input boxes and checkboxes
        self.myIngameIDs = []
        self.myIngameIDs.append(self.ingameID1.text.lower())
        self.myIngameIDs.append(self.ingameID2.text.lower())
        self.myIngameIDs.append(self.ingameID3.text.lower())
        self.myIngameIDs.append(self.ingameID4.text.lower())
        self.myIngameIDs.append(self.ingameID5.text.lower())
        self.myIngameIDs.append(self.ingameID6.text.lower())
        self.preText = self.customPreText.text
        self.postText = self.customPostText.text
        self.includeRaces = int(self.showRaceBox.active)
        self.includeOpponentName = int(self.showOppNameBox.active)
        self.includeTimeStamp = int(self.showTimestampBox.active)
        self.allowUpdateWhileInReplay = int(self.updateTitleReplayBox.active)

        #this will try to convert the string to an integer, but if the user enters something wrongly, it will set the interval to default
        try:
            timeInterval = int(self.titleUpdateIntervalText.text)
        except:
            timeInterval = 10
        #this will normalize the interval between 10 and 30 seconds
        timeInterval = min(max(timeInterval, 30),10)

        self.clientID = self.clientIDText.text
        self.oauth = self.oAUTHText.text
        self.twitchChannel = self.twitchNameText.text

        #gameurl and uiurl are the address for the sc2 api, the header for the update is already prepared
        GAMEurl = "http://localhost:6119/game"
        UIurl = "http://localhost:6119/ui"
        headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Authorization':'OAuth ' + self.oauth, 'Client-ID':self.clientID}
        try:
            automatedString = ""

            GAMEresponse = requests.get(GAMEurl, timeout=100).json()
            UIresponse = requests.get(UIurl, timeout=100).json()
            #print(GAMEresponse)
            #print(UIresponse)
            analyse = 0
            if len(GAMEresponse["players"]) == 2: #activate script if 2 players are playing right now
                if GAMEresponse["isReplay"]:
                    if self.allowUpdateWhileInReplay: #activate script if in replay and variable is =1
                        analyse = 1
                else:
                    analyse = 1
            if analyse == 1:
                race1 = GAMEresponse["players"][0]["race"][0].upper() #reduce race of player1 to first letter and capitalize, so 'T'erran
                race2 = GAMEresponse["players"][1]["race"][0].upper() #reduce race of player2 to first letter and capitalize, so 'P'rotoss
                name1 = GAMEresponse["players"][0]["name"] #player1 name
                name2 = GAMEresponse["players"][1]["name"] #player2 name
                victorious = GAMEresponse["players"][0]["result"]
                if name1.lower() in self.myIngameIDs: #if i am player1, do nothing
                    name1 = ""
                elif name2.lower() in self.myIngameIDs: #if i am player 2, swap names and races in position (so its TvZ instead of ZvT if i play terran)
                    race1, race2 = race2, race1
                    name2 = name1
                    name1 = ""
                else:
                    name1 = "- " + name1 + " " #if my name is not found in "myIngameIDs" then i am an observer casting a match

                if self.includeRaces == 1: #include races in stream title if variable is set to =1
                    automatedString = race1 + "v" + race2 + " "

                if self.includeOpponentName and not GAMEresponse["isReplay"]: #include opponent name in stream title if variable is set to =1
                    automatedString += name1 + "vs " + name2 + " "
                        
                ingameTime = ""
                if GAMEresponse["isReplay"]: #edit "ingameTime" string to depends if in replay or not
                    ingameTime = "in Replay"
                else:
                    ingameTime = "at " + str(int(GAMEresponse["displayTime"]/60)) + "min"
                if self.includeTimeStamp:
                    automatedString += ingameTime + " "

                if victorious != "Undecided": #if game is over and i am in score screen or matchmaking queue, then only put "preText + postText" in stream title
                    automatedString = ""
                if UIresponse["activeScreens"] != [] and GAMEresponse["isReplay"] or not self.allowUpdateWhileInReplay and GAMEresponse["isReplay"]: #when you watched a replay and go back to main screen, it still shows as "replay = True" but the UI does not say ingame
                    automatedString = ""

                automatedString = self.preText + " " + automatedString + self.postText
                if self.lastPutString != automatedString: #if last updated string is not identical to newly constructed string, then update stream title!
                    params = {'channel[status]': automatedString}
                    r = requests.put('https://api.twitch.tv/kraken/channels/' + self.twitchChannel, headers = headers, params = params).raise_for_status()
                    self.lastPutString = automatedString
                    self.streamTitleUpdateText.text = self.lastPutString
                    print("Updated stream title with: " + automatedString.encode("ascii", "ignore").decode())
        except requests.exceptions.ConnectionError: #handle exception when starcraft is detected as not running
            print("StarCraft 2 not running!")
        except ValueError:
            print("StarCraft 2 starting.")
        return 1

    def updateExampleTitle(self):
        #the example title text will be instantly updated once any change to the following happen
        self.preText = self.customPreText.text
        self.postText = self.customPostText.text
        self.includeRaces = int(self.showRaceBox.active)
        self.includeOpponentName = int(self.showOppNameBox.active)
        self.includeTimeStamp = int(self.showTimestampBox.active)
        self.exampleTitleText.text = self.preText + ' ' + 'TvT '*self.includeRaces + 'vs BuRny '*self.includeOpponentName + 'at 15min '*self.includeTimeStamp + self.postText

    def scriptToggle(self):
        #i guess this variable is not used sadly
        self.scriptActive = self.scriptActiveBox.active

    def ClientIDbtnPressed(self):
        #the first button
        webbrowser.open("https://www.twitch.tv/kraken/oauth2/clients/new")

    def OAuthbtnPressed(self):
        #the 2nd button
        webbrowser.open("https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=" + self.clientIDText.text + "&redirect_uri=http://localhost&scope=channel_editor")

    def twitchLinkbtnPressed(self):
        #3rd button, who would've guessed? :P
        webbrowser.open("https://www.twitch.tv/" + self.twitchNameText.text.lower()+"/dashboard")

    def loadSettings(self):
        #this will try to load the config file, but it will only work if it exists, and if the config file hasn't been manipulated
        try:
            lines = [line.rstrip('\n') for line in open('titleUpdater.cfg')]
            self.clientIDText.text = lines[0]
            self.oAUTHText.text = lines[1]
            self.twitchNameText.text = lines[2]
            self.ingameID1.text = lines[3]
            self.ingameID2.text = lines[4]
            self.ingameID3.text = lines[5]
            self.ingameID4.text = lines[6]
            self.ingameID5.text = lines[7]
            self.ingameID6.text = lines[8]
            self.customPreText.text = lines[9]
            self.customPostText.text = lines[10]
            self.showRaceBox.active = bool(int(lines[11]))
            self.showOppNameBox.active = bool(int(lines[12]))
            self.showTimestampBox.active = bool(int(lines[13]))
            self.updateTitleReplayBox.active = bool(int(lines[14]))

            #this here will again try to put the default time interval
            try:
                self.titleUpdateIntervalText.text = lines[15]
            except:
                self.titleUpdateIntervalText.text = "10"
        except: pass

    def saveSettings(self, dt):
        global timeInterval
        #"try" in case it doesn't have admin rights for some reason, or if the script for any other reason can't write to file
        try:
            self.tempSettings = [self.clientID, self.oauth, self.twitchChannel, self.myIngameIDs[0], self.myIngameIDs[1], self.myIngameIDs[2], self.myIngameIDs[3], self.myIngameIDs[4], self.myIngameIDs[5], self.preText, self.postText, str(self.includeRaces), str(self.includeOpponentName), str(self.includeTimeStamp), str(self.allowUpdateWhileInReplay), str(timeInterval)]
            if self.tempSettings != self.tempSettings2:
                f = open("titleUpdater.cfg",'w')
                for i in self.tempSettings:
                    f.write(i + "\n")
                f.close()
                self.tempSettings2 = self.tempSettings
        except: pass

class TitleUpdaterApp(App):
    #this is just the GUI builder if i understand correctly
    def build(self):
        global timeInterval
        game = TitleUpdater()
        game.init2()
        game.loadSettings()
        Clock.schedule_interval(game.update, timeInterval)
        Clock.schedule_interval(game.saveSettings, 20)
        return game

if __name__ == '__main__':
    TitleUpdaterApp().run()