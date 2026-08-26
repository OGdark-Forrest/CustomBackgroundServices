from utils.imports import *
from fastapi import APIRouter, Header
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general, psutil

router = APIRouter()

@router.put("/server/restart")
def getGroupRun(deviceID: str = Header(), deviceKey: str = Header()):
    verifyKey(deviceID, deviceKey)

    info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
    info["serverStatus"] = "3"
    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)