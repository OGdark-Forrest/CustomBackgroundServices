import utils.general as general

info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
info["boot"] = "0"
general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)