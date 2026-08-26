from utils.imports import *
from fastapi import APIRouter, Header
from ..service.operations import PlaybackManager
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general

router = APIRouter()

player = PlaybackManager()

async def runLoop():
    await player.setManager()

    try:
        while True:
            await player.checkPlaybackStatus(disableNotification=True)
            await asyncio.sleep(2)

    except asyncio.CancelledError:
        general.notificationThread("Server")


@router.put("/player/toggle")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    await player.toggle()

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/right")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("right")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/left")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("left")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/up")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("up")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/down")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("down")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/enter")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("enter")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/tab")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("tab")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }

@router.put("/player/mute")
async def togglePlayback(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemotePlayer")
    verifyKey(deviceID, deviceKey)

    pyautogui.press("volumemute")

    return {
        "status code": 200,
        "content": "Action Performed Successfully"
    }