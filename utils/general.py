from utils.imports import *

def readJSON(filename):
    with open(filename) as rfile:
        data = json.load(rfile)
    return data

def writeJSON(filename, data):
    with open(filename, "w") as wfile:
        json.dump(data, wfile, indent=4)

def writeTXT(filename, data):
    with open(filename, "w", encoding="utf-8") as wfile:
        wfile.write(data)

def readTXT(filename):
    with open(filename, "r", encoding="utf-8") as rfile:
        data = rfile.read()
    return data

def getResponse(sessionObj, requestType, endpoint, params={}):
    while True:
        headers = {
            "Authorization": f"Bearer {sessionObj.accessToken}"
        }
        try:
            if requestType == "PUT":
                response = requests.put(
                    f"https://api.spotify.com/v1/{endpoint}",
                    headers=headers,
                    params=params
                )
            elif requestType == "POST":
                response = requests.post(
                    f"https://api.spotify.com/v1/{endpoint}",
                    headers=headers,
                    params=params
                )            
            elif requestType == "GET":
                response = requests.get(
                    f"https://api.spotify.com/v1/{endpoint}",
                    headers=headers,
                    params=params
                )    
            if response.status_code == 401:
                print("Access token expired, refreshing")
                sessionObj.restoreValidity()
                print("Successfully refreshed")
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
    return response

def notificationThread(header, message=None):
    threading.Thread(
    target=toast,
    args=(header, message),
    daemon=True
    ).start()

def checkRunning(SERVICE):
    serviceInfo = readJSON(pathInfo("jsonUtils")+"services.json")

    if SERVICE in serviceInfo:
        for service in serviceInfo[SERVICE]:
            running = serviceInfo[SERVICE][service]["running"]
            if running == "True":
                return True
        else:
            return False

    for group in serviceInfo:
        for service in serviceInfo[group]:
            if service == SERVICE:
                running = serviceInfo[group][service]["running"]
                if running == "True":
                    return True
                else:
                    return False

def raiseServerError(service):
    if not checkRunning(service):
        raise HTTPException(404, detail="Service not running")

def pathInfo(category):
    """
    Categories: jsonAuth, jsonService, jsonUtils, logs, custom, vbs
    """
    return readJSON("utils/jsonFiles/utils/filePath.json")[category]

def setLogger(name):
    return logging.getLogger(name)

def configureLogger(fileName):
    logging.basicConfig(
        filename=f"utils/logs/{fileName}",
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def generate_session_id(device_key):
    time_window = int(time.time() // 120)

    return hmac.new(
        device_key.encode(),
        str(time_window).encode(),
        hashlib.sha256
    ).hexdigest()

def addProcess(serviceName, pid):
    servicePID = readJSON(pathInfo("jsonUtils")+"serviceProcesses.json")
    servicePID[serviceName] = [pid]
    writeJSON(pathInfo("jsonUtils")+"serviceProcesses.json", servicePID)