import requests
import time

#text after a hash sign are comments by me

#how "preText" and "postText" work: [EU]Master2 TvT vs Pundurs at 3min Tune in for some fun!
#I guess you can figure out what the preText and postText does!
preText = "[EU]Master2"
postText = "Tune in for some fun!"
myIngameIDs = ["BuRny", "Burny", "Blubb", "Bla"] #the script needs to know which usernames you have ingame so replace your ingame usernames (NA / EU / KR server or barcodes) so that it can list your opponent in the stream title, is case sensitive!
#if you don't add any ID and have an empty list (myIngameIDs = []) then your name might be accidently listed in the stream title
#also if the script can't detect your ingame name, then the stream title (assuming you are zerg) might say TvZ instead of ZvT (it lists your race first)

twitchChannel = "burnysc2" #replace the name with your twitch name, it has to be surrounded by the quotation marks "
oauth = "nf9m45g45bg45bg49c77s1xo" #replace the channel editor token from step 3), surrounded by quotation marks "
clientID = "l3jijexx6g43bg34bgre1ddv8x5j5nsm" #replace the Client ID from step 2), surrounded by quotation marks "

allowUpdateWhileInReplay = 1 #change to 0 if stream title should NOT be updated while in replay
includeRaces = 1 #change to 0 if stream title should NOT include the races/matchup
includeOpponentName = 1 #change to 0 if the opponent name should NOT be included in the stream title
includeTimeStamp = 1 #change to 0 if the ingame timer should NOT be included in the stream title
timeInterval = 10 #this number indicates how long the script sleeps (in seconds) between each check (the script checks if you are in a new match or if the game timer increased), don't put it lower than 5


#----------- DONT TOUCH ANYTHING BELOW THIS UNLESS YOU KNOW WHAT YOU ARE DOING -------------#
GAMEurl = "http://localhost:6119/game"
UIurl = "http://localhost:6119/ui"
headers = {'Accept':'application/vnd.twitchtv.v3+json', 'Authorization':'OAuth ' + oauth, 'Client-ID':clientID}
lastPutString = ""
while 1:
    time.sleep(timeInterval)
    try:
        automatedString = ""

        GAMEresponse = requests.get(GAMEurl, timeout=100).json()
        UIresponse = requests.get(UIurl, timeout=100).json()
        #GAMEresponse = requests.get(html.unescape(GAMEurl), timeout=100).json()
        analyse = 0
        if len(GAMEresponse["players"]) == 2: #activate script if 2 players are playing right now
            if GAMEresponse["isReplay"]:
                if allowUpdateWhileInReplay: #activate script if in replay and variable is =1
                    analyse = 1
            else:
                analyse = 1
        if analyse == 1:
            race1 = GAMEresponse["players"][0]["race"][0].upper() #reduce race of player1 to first letter and capitalize, so 'T'erran
            race2 = GAMEresponse["players"][1]["race"][0].upper() #reduce race of player2 to first letter and capitalize, so 'P'rotoss
            name1 = GAMEresponse["players"][0]["name"] #player1 name
            name2 = GAMEresponse["players"][1]["name"] #player2 name
            victorious = GAMEresponse["players"][0]["result"]
            if name1 in myIngameIDs: #if i am player1, do nothing
                name1 = ""
            elif name2 in myIngameIDs: #if i am player 2, swap names and races in position (so its TvZ instead of ZvT if i play terran)
                race1, race2 = race2, race1
                name2 = name1
                name1 = ""
            else:
                name1 = "- " + name1 + " " #if my name is not found in "myIngameIDs" then i am an observer casting a match

            if includeRaces == 1: #include races in stream title if variable is set to =1
                automatedString = race1 + "v" + race2 + " "

            if includeOpponentName and not GAMEresponse["isReplay"]: #include opponent name in stream title if variable is set to =1
                automatedString += name1 + "vs " + name2 + " "
                    
            ingameTime = ""
            if GAMEresponse["isReplay"]: #edit "ingameTime" string to depends if in replay or not
                ingameTime = "in Replay"
            else:
                ingameTime = "at " + str(int(GAMEresponse["displayTime"]/60)) + "min"
            if includeTimeStamp:
                automatedString += ingameTime + " "

            if victorious != "Undecided": #if game is over and i am in score screen or matchmaking queue, then only put "preText + postText" in stream title
                automatedString = ""
            if UIresponse["activeScreens"] != [] and GAMEresponse["isReplay"]: #when you watched a replay and go back to main screen, it still shows as "replay = True" but the UI does not say ingame
                automatedString = ""

            automatedString = preText + " " + automatedString + postText
            if lastPutString != automatedString: #if last updated string is not identical to newly constructed string, then update stream title!
                params = {'channel[status]': automatedString}
                r = requests.put('https://api.twitch.tv/kraken/channels/' + twitchChannel, headers = headers, params = params).raise_for_status()
                lastPutString = automatedString
                print("Updated stream title with: " + automatedString.encode("ascii", "ignore").decode())
    except requests.exceptions.ConnectionError: #handle exception when starcraft is detected as not running
        print("StarCraft 2 not running!")
    except ValueError:
        print("StarCraft 2 starting.")
#----------- DONT TOUCH ANYTHING ABOVE THIS UNLESS YOU KNOW WHAT YOU ARE DOING -------------#