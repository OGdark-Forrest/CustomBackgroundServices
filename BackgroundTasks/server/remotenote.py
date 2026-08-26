from utils.imports import *

from fastapi import APIRouter, Header
from pydantic import BaseModel
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general

router = APIRouter()

class Note(BaseModel):
    content: str

@router.get("/notes/getFiles")
def getFiles(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)
    folder = Path("C:/Users/meerc/Documents/SharedNotes")
    files = [f.name[:-4] for f in folder.iterdir() if f.is_file()]
    return files

@router.get("/notes/get")
def getNotes(filename: str, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)
    return {
        "status code": 200,
        "content": general.readTXT(f"C:/Users/meerc/Documents/SharedNotes/{filename}.txt")
    }

@router.post("/notes/post")
def postNotes(content: Note, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteNotes")
    verifyKey(deviceID, deviceKey)

    text = content.content

    filename = text[:text.find("\n")]
    text = text[text.find("\n"):]

    general.writeTXT(f"C:/Users/meerc/Documents/SharedNotes/{filename}.txt", text)

    general.notificationThread(f"{filename}.txt succesfully received")