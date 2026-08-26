from utils.imports import *
from ServiceCalls.Server.serverauth import verifyKey, getKey
import utils.general as general

router = APIRouter()

sct = mss.mss()

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

def set_brightness(value):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()
    for method in methods:
        method.WmiSetBrightness(Brightness=value, Timeout=1)

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

@router.put("/lock")
def lockScreen(deviceID: str = Header(), deviceKey: str = Header()):
    verifyKey(deviceID, deviceKey)
    ctypes.windll.user32.LockWorkStation()

@router.put("/setlum")
def setBrightness(deviceID: str = Header(), deviceKey: str = Header(), brightness: int = 0):
    verifyKey(deviceID, deviceKey)
    try:
        set_brightness(brightness)
        with monitorcontrol.get_monitors()[0] as monitor:
            monitor.set_luminance(brightness)
    except:
        pass

@router.get("/getSS")
def getScreenShot(
    deviceID: str | None = Header(default=None),
    deviceKey: str | None = Header(default=None),
    sessionID: str | None = Header(default=None)
):
    if deviceKey:
        verifyKey(deviceID, deviceKey)
    else:
        deviceKey = getKey(deviceID)
        intendedSessionID = general.generate_session_id(deviceKey)
        if hmac.compare_digest(intendedSessionID, sessionID) is False:
            raise HTTPException(401, "Invalid device ID/Key")
        
    shot = sct.grab(sct.monitors[1])

    image = Image.frombytes(
        "RGB",
        shot.size,
        shot.bgra,
        "raw",
        "BGRX"
    )

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=40)

    return Response(
        content=buffer.getvalue(),
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-store"
        }
    )

@router.get("/screenShare")
def create_screen_share(
    deviceID: str = Header(),
    deviceKey: str = Header()
):
    verifyKey(deviceID, deviceKey)

    sessionID = general.generate_session_id(deviceKey)

    return {
        "url": f"https://aetherlink.uk/screenShare/{deviceID}/{sessionID}"
    }

@router.get("/screenShare/{deviceID}/{sessionID}")
def screen_share_page(deviceID: str, sessionID: str):

    deviceKey = getKey(deviceID)

    expected = general.generate_session_id(deviceKey)

    if not hmac.compare_digest(expected, sessionID):
        raise HTTPException(401, "Invalid session")

    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Laptop Screen</title>

        <style>
            body {
                margin: 0;
                background: black;
                overflow: hidden;
            }

            #screen {
                width: 100vw;
                height: 100vh;
                object-fit: contain;
            }
        </style>
    </head>

    <body>
        <img id="screen">

        <script>
            async function updateScreen() {
                while (true) {
                    const response = await fetch("/getSS", {
                        headers: {
                            "deviceID": "%s",
                            "sessionID": "%s"
                        },
                        cache: "no-store"
                    });

                    if (!response.ok) {
                        console.log("Request failed:", response.status);
                        await new Promise(r => setTimeout(r, 750));
                        continue;
                    }

                    const blob = await response.blob();

                    const image = document.getElementById("screen");

                    image.src = URL.createObjectURL(blob);

                    await new Promise(resolve => {
                        image.onload = resolve;
                    });
                }
            }

updateScreen();

            updateScreen();

            setInterval(updateScreen, 250);
        </script>
    </body>
    </html>
    """ % (deviceID, sessionID))