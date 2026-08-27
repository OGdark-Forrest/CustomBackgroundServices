from utils.imports import *
import utils.general as general

general.configureLogger("stdout.log")
logger = general.setLogger("Server.ServerManager")

def runServer():
    global serverProcess
    serverProcess = subprocess.Popen(
        [general.pathInfo("pyw"), "-m", "ServiceCalls.Server.server"],
        cwd=general.pathInfo("custom")
    )

def runCloudFlared():
    subprocess.Popen(
        ["powershell", "-NoExit", "-Command", "cloudflared tunnel run aetherlink"],
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.CREATE_NO_WINDOW
    )

def run():
    global serverProcess
    serverProcess = None
    
    runServer()
    logger.info("Starting FastAPI server")
    general.notificationThread("Server started...")
    runCloudFlared()
    logger.info("Starting Cloudflared Tunnel")
    general.notificationThread("Tunnel started...")

    while True:
        info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
        condition = info["serverStatus"]

        if condition == "1":
            if serverProcess:
                serverProcess.terminate()
                serverProcess = None
                general.notificationThread("Server stopped...")

        elif condition == "2":
            if serverProcess is None:
                runServer()
                general.notificationThread("Server started...")

        elif condition == "3":
            if serverProcess is None:
                runServer()
            else:
                serverProcess.terminate()
                time.sleep(2)
                runServer()
            general.notificationThread("Server restarted...")

        info["serverStatus"] = "0"
        general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

        time.sleep(1)

if __name__ == "__main__":
    run()