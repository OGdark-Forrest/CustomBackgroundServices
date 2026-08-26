from utils.imports import *
import utils.general as general

class PlaybackManager:
    def __init__(self):
        self.currSession = None
        self.mode = None
        self.PLAYING = GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING

    async def setManager(self):
        self.sessionManager = await GlobalSystemMediaTransportControlsSessionManager.request_async()

    async def checkPlaybackStatus(self, app="", disableNotification=False):
        self.sessions = self.sessionManager.get_sessions()
        message = (f"No Active {app} Session Detected", "Please start a media session")

        if len(self.sessions) == 0:
            if not disableNotification:
                general.notificationThread(*message)
            self.currSession = None
            return False

        if not app:
            self.currSession = self.sessionManager.get_current_session()
            if not self.currSession:
                return False
            return True
        
        for session in self.sessions:
            if app in session.source_app_user_model_id:
                self.currSession = session
                return True

        if not disableNotification:
            general.notificationThread(*message)

        self.currSession = None
        return False

    async def toggle(self):
        print("Called")
        print(self.currSession)
        if not self.currSession:
            return
        print("toggling")
        await self.currSession.try_toggle_play_pause_async()

    async def nextSong(self):
        if not self.currSession:
            return
        await self.currSession.try_skip_next_async()

    async def prevSong(self):
        if not self.currSession:
            return
        await self.currSession.try_skip_previous_async()

    async def skipTo(self, ms):
        if not self.currSession:
            return
        await self.currSession.try_change_playback_position_async(ms*10000)