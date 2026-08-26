from utils.imports import *
from fastapi import APIRouter, Header
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general, psutil

router = APIRouter()

def readData():
    return general.readJSON(general.pathInfo("jsonUtils")+"services.json")

@router.get("/services/getGroupsRun")
def getGroupRun(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    groupList = []
    for group in serviceInfo:
        for service in serviceInfo[group]:
            if serviceInfo[group][service]["running"] == "False":
                groupList.append(group)
                break

    return groupList

@router.get("/services/getServicesRun")
def getServicesRun(group, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    serviceList = []
    for service in serviceInfo[group]:
        if serviceInfo[group][service]["running"] == "False":
            serviceList.append(service)

    return serviceList

@router.put("/services/runService")
def runService(group, service, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    serviceInfo[group][service]["running"] = "True"
    general.writeJSON(general.pathInfo("jsonUtils")+"services.json", serviceInfo)

@router.get("/services/getGroupsStop")
def getGroupStop(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    groupList = []
    for group in serviceInfo:
        for service in serviceInfo[group]:
            if serviceInfo[group][service]["running"] == "True":
                groupList.append(group)
                break

    return groupList

@router.get("/services/getServicesStop")
def getServicesStop(group, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    serviceList = []
    for service in serviceInfo[group]:
        if serviceInfo[group][service]["running"] == "True":
            serviceList.append(service)

    return serviceList

@router.put("/services/StopService")
def StopService(group, service, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteService")
    verifyKey(deviceID, deviceKey)
    serviceInfo = readData()
    serviceInfo[group][service]["running"] = "False"
    general.writeJSON(general.pathInfo("jsonUtils")+"services.json", serviceInfo)