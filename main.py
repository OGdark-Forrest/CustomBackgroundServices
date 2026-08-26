from GUI import selector
from utils import general
import subprocess

info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
status = info["boot"]
general.configureLogger("stdout.log")
logger = general.setLogger("main.py")

if status == "0":
    logger.info("Boot Status: 0")
    serviceInfo = general.readJSON(general.pathInfo("jsonUtils")+"services.json")
    listFiles = []

    for group in serviceInfo:
        for service in serviceInfo[group]:
            fname = serviceInfo[group][service]["fileName"]
            listFiles.append(f"ServiceCalls.{group}.{fname}")

            if group == "Server":
                break
    logger.debug(f"Services: {listFiles}")

    for file in listFiles:
        process = subprocess.Popen(
            [
                general.pathInfo("pyw"),
                "-m",
                file
            ],
            cwd=general.pathInfo("custom"),
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        logger.debug(f"Started process {file}")

    info["boot"] = "1"
    general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

subprocess.Popen(
    ["wscript.exe", general.pathInfo("vbs")+"MiniOverlay.vbs"],
    cwd=general.pathInfo("custom"),
    creationflags=subprocess.CREATE_NO_WINDOW
)

selector.run()