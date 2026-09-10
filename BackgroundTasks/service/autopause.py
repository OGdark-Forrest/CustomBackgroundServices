from .operations import PlaybackManager
from utils.imports import *
import utils.general as general

class Monitor:
    def __init__(self):
        self.playbackManager = PlaybackManager()
        self.PLAYING = GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
        self.continuePlaying = False

    async def setMediaManager(self):
        await self.playbackManager.setManager()

    async def checkToggleSession(self):
        if not await self.playbackManager.checkPlaybackStatus("Spotify", True):
            return False

        spotSessionPlaying = self.playbackManager.currSession.get_playback_info().playback_status == self.PLAYING
        if not spotSessionPlaying:
            return True
        
        for session in self.playbackManager.sessions:
            if "Spotify" in session.source_app_user_model_id:
                continue
            if session.get_playback_info().playback_status != self.PLAYING or self.continuePlaying is True:
                continue
            
            await self.playbackManager.toggle()
            self.continuePlaying = True

        return True

    async def checkContinue(self):
        for session in self.playbackManager.sessions:
            if session.get_playback_info().playback_status == self.PLAYING:
                return

        if self.continuePlaying:
            await self.playbackManager.toggle()
            self.continuePlaying = False

async def run():
    monitor = Monitor()
    await monitor.setMediaManager()
    while True:
        condition = general.checkRunning("AutoPause")
        if not condition:
            await asyncio.sleep(1)
            continue
        sessionExists = await monitor.checkToggleSession()
        if sessionExists:
            await monitor.checkContinue()

        await asyncio.sleep(1)