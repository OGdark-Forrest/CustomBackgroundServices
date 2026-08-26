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

    async def checkSession(self):
        if not await self.playbackManager.checkPlaybackStatus("Spotify", True):
            return False, False

        spotSessionPlaying = self.playbackManager.currSession.get_playback_info().playback_status == self.PLAYING

        if not spotSessionPlaying:
            return True, False
        
        for session in self.playbackManager.sessions:
            if "Spotify" in session.source_app_user_model_id:
                continue
            if session.get_playback_info().playback_status != self.PLAYING:
                continue

            await self.playbackManager.toggle()
            self.continuePlaying = True

        return True, False

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
        sessionExists, sessionPlaying = await monitor.checkSession()
        if sessionExists and not sessionPlaying:
            await monitor.checkContinue()

        await asyncio.sleep(1)