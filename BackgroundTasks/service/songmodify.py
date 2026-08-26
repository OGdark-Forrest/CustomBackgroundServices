from BackgroundTasks.service import songauth
from utils import general

class ModifySession():
    def __init__(self):
        self.accessToken = None

        self.songFile = general.pathInfo("jsonService")+"songTimes.json"

    def start(self):
        self.restoreValidity()

    def restoreValidity(self):
        result = songauth.token_valid()

        if not result["valid"]:
            if not result["created"]:
                songauth.set_spotify_playback_token()
            else:
                songauth.refresh_access_token()
            return self.restoreValidity()

        self.accessToken = result["accessToken"]

#-------------------------------------------------------------------------------------------------------------------------------------------------------

    def convertToStandard(self, time):
        timeSeconds = time/1000
        minutes = timeSeconds//60
        seconds = timeSeconds - minutes*60

        formattedMin = str(int(minutes))
        if int(seconds) == 0:
            formattedSec = "00"
        elif int(seconds) < 10:
            formattedSec = f"0{int(seconds)}"
        else:
            formattedSec = str(int(seconds))

        return f"{formattedMin}:{formattedSec}"

    def breakTime(self, inputTime: str, id):
        if inputTime == "start":
            return 0
        elif inputTime == "end":
            return self.getSongDuration(id)

        min, sec = inputTime.split(":")

        return (60*int(min) + int(sec))*1000

#-------------------------------------------------------------------------------------------------------------------------------------------------------

    def logSongEntry(self, timeInterval: list, artistName: list, songName, id):
        self.getSongs()
        self.songData[id] = (timeInterval, artistName, songName)
        general.writeJSON(self.songFile, self.songData)

    def checkTimes(self, timeStart, timeEnd, id):
        milliStart, milliEnd = self.breakTime(timeStart, id), self.breakTime(timeEnd, id)

        if milliEnd < milliStart or milliEnd > self.getSongDuration(id):
            return False
        
        return milliStart, milliEnd

    def getSongID(self, songName, artistName):
        query = f"track:{songName} artist:{artistName}"
        response = general.getResponse(
            sessionObj=self, 
            requestType="GET", 
            endpoint="search",
            params={
                "q": query,
                "type": "track",
                "limit": 1
            })
        data = response.json()

        if data["tracks"]["items"]:
            track = data["tracks"]["items"][0]
            id = track["id"]
            songName = track["name"]
            artistName = [artist["name"] for artist in track["artists"]]
            return id, songName, artistName

    def getSongDuration(self, id):
        response = general.getResponse(
            sessionObj=self,
            requestType="GET",
            endpoint=f"tracks/{id}"
        )

        return response.json()["duration_ms"]

    def searchSong(self, song, artist):
        q = f"track:{song} artist:{artist}"
        response = general.getResponse(
            sessionObj=self,
            requestType="GET",
            endpoint="search",
            params={
                "q": q,
                "type": "track",
                "limit": 1
            }
        )
        data = response.json()
        track = data["tracks"]["items"][0]

        song_name = track["name"]
        artists = [artist["name"] for artist in track["artists"]]

        return song_name, artists

#-------------------------------------------------------------------------------------------------------------------------------------------------------

    def getSongs(self):
        self.songData = general.readJSON(self.songFile)

    def removeEntry(self, id):
        self.getSongs()
        self.songData.pop(id)
        general.writeJSON(self.songFile, self.songData)

    def modifyEntry(self, id, timeStart, timeEnd):
        self.getSongs()
        milliStart, milliEnd = self.breakTime(timeStart), self.breakTime(timeEnd)

        if milliEnd < milliStart or milliEnd > self.getSongDuration(id):
            return ("Invalid Times")

        self.songData[id] = [[milliStart, milliEnd]] + self.songData[id][1:]
        general.writeJSON(self.songFile, self.songData)