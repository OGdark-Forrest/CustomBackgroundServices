import utils.general as general
from .operations import PlaybackManager
from utils.imports import *

class MonitorSession:
    def __init__(self):
        self.songTimes = None

        self.currTime = None
        self.songName = None

        self.songFile = general.pathInfo("jsonService")+"songTimes.json"
        self.PLAYING = GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

    async def setPlaybackInfo(self):
        timeline = self.player.currSession.get_timeline_properties()
        self.currTime = timeline.position.total_seconds()*1000

        info = await self.player.currSession.try_get_media_properties_async()
        self.songName = info.title

    async def checkPosition(self):
        await self.setPlaybackInfo()
        for entry in self.songTimes:
            if self.songTimes[entry][2] == self.songName:
                start, end = self.songTimes[entry][0]
                if start < self.currTime < end:
                    currentStatus = self.player.currSession.get_playback_info().playback_status
                    if currentStatus != self.PLAYING:
                        continue
                    await self.player.skipTo(end-200)

    def readSongs(self):
        self.songTimes = general.readJSON(self.songFile)

async def run():
    sesh = MonitorSession()
    sesh.player = PlaybackManager()
    await sesh.player.setManager()
    while True:
        running = general.checkRunning("IntervalSkipper")
        if not running:
            await asyncio.sleep(1)
            continue

        sesh.readSongs()

        result = await sesh.player.checkPlaybackStatus(app="Spotify", disableNotification=True)

        if not result:
            await asyncio.sleep(1)
            continue

        await sesh.checkPosition()
        await asyncio.sleep(1)