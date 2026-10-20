from utils.imports import *

from fastapi import APIRouter, Header
from pydantic import BaseModel
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general

router = APIRouter()

sharedNotesDirectory = "C:/Users/meerc/Documents/SharedNotes"

class Note(BaseModel):
    content: str

@router.get("/notes/getFiles")
def getFiles(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)
    folder = Path(sharedNotesDirectory)
    files = [f.name for f in folder.iterdir() if f.is_file()]
    return files

@router.get("/notes/get")
def getNotes(filename: str, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)
    return {
        "status code": 200,
        "content": general.readTXT(f"{sharedNotesDirectory}/{filename}")
    }

@router.post("/notes/post")
def postNotes(content: Note, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)

    text = content.content

    filename = text[:text.find("\n")]
    text = text[text.find("\n"):]

    general.writeTXT(f"{sharedNotesDirectory}/{filename}", text)

    general.notificationThread(f"{filename}.txt succesfully received")