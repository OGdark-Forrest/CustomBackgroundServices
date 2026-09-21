import utils.general as general
import json

try:
    info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
    info["boot"] = "0"
    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)
except:
    info = {
        "boot": "0",
        "serverStatus": "2",
        "mode": ""
    }
    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)