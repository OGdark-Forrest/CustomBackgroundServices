from utils.imports import *
from ServiceCalls.Server.serverauth import verifyKey, getKey
import utils.general as general, psutil

router = APIRouter()

sct = mss.mss()

@router.put("/server/restart")
def getGroupRun(deviceID: str = Header(), deviceKey: str = Header()):
    verifyKey(deviceID, deviceKey)

    info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
    info["serverStatus"] = "3"
    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

@router.put("/lock")
def lockScreen(deviceID: str = Header(), deviceKey: str = Header()):
    verifyKey(deviceID, deviceKey)
    ctypes.windll.user32.LockWorkStation()

def set_brightness(value):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()
    for method in methods:
        method.WmiSetBrightness(Brightness=value, Timeout=1)

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