from utils.imports import *
from ServiceCalls.Server.serverauth import verifyKey
import utils.general as general

router = APIRouter()

def set_brightness(value):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()
    for method in methods:
        method.WmiSetBrightness(Brightness=value, Timeout=1)

def readData(mode):
    return general.readJSON(general.pathInfo("jsonService")+"siteApps.json")[mode]

def launch_shortcut(path):
    global serviceManagerProcess
    subprocess.Popen(
        ["cmd", "/c", "start", "", path],
        shell=False,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

@router.put("/mode/start")
def startTasks(mode, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteStart")
    verifyKey(deviceID, deviceKey)
    info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
    currMode = info["mode"]
    if currMode == mode:
        raise HTTPException(status_code=404, detail="Already in this mode")

    if currMode != "":
        return

    data = readData(mode)

    apps, sites, services = data["Apps"], data["Websites"], data["Services"]

    brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

    if sites:
        subprocess.Popen([brave_path, *sites], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)

    for app in apps:
        launch_shortcut(app)

    serviceInfo = general.readJSON(general.pathInfo("jsonUtils")+"services.json")

    for service in services:
        group, name = service.split("/")
        print(group, name)
        serviceInfo[group][name]["running"] = "True"

    general.writeJSON(general.pathInfo("jsonUtils")+"services.json", serviceInfo)
    info["mode"] = mode

    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

    return {"status code": HTTPException(200)}

@router.put("/mode/close")
def closeTasks(full: bool, deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteStart")
    verifyKey(deviceID, deviceKey)
    info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
    mode = info["mode"]

    if mode:
        data = readData(mode)
        appList = data["Closing"]
    else:
        appList = [
            "brave.exe",
            "Code.exe",
            "Obsidian.exe",
            "Spotify.exe",
            "Notepad.exe"
        ]

    for proc in psutil.process_iter():
        if proc.name() not in appList:
            continue
        try:
            proc.terminate()
        except:
            continue

    serviceInfo = general.readJSON(general.pathInfo("jsonUtils")+"services.json")

    info["mode"] = ""

    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

    pyautogui.hotkey("win", "d")

    if full == True:
        for group in serviceInfo:
            for service in serviceInfo[group]:
                if service == "RemoteService" or service == "RemoteStart":
                    continue
                serviceInfo[group][service]["running"] = "False"
        general.writeJSON(general.pathInfo("jsonUtils")+"services.json", serviceInfo)
        ctypes.windll.user32.LockWorkStation()
        if datetime.datetime.now() >= 22:
            set_brightness(30)

@router.get("/mode/getall")
def getModes(deviceID: str = Header(), deviceKey: str = Header()):
    general.raiseServerError("RemoteStart")
    verifyKey(deviceID, deviceKey)
    modeList = []
    data = general.readJSON(general.pathInfo("jsonService")+"siteApps.json")
    for mode in data:
        modeList.append(mode)

    return modeList
