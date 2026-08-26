from BackgroundTasks.server import remoteplayer, remoteserver, remoteservice, remotestart, remotenote
from utils.imports import *
import utils.general as general

from BackgroundTasks.service.app import app

from ServiceCalls.Server import register
from GUI import chat, selector, curl


if sys.stdout is None:
    sys.stdout = open(general.pathInfo("logs")+"server_stdout.log", "a")
if sys.stderr is None:
    sys.stderr = open(general.pathInfo("logs")+"server_stderr.log", "a")

tasks = []

serviceMap = {
    "RemotePlayer": [remoteplayer.router, remoteplayer.runLoop],
    "RemoteNotes": [remotenote.router, None],
    "RemoteStart": [remotestart.router, None],
    "RemoteService": [remoteservice.router, None]
}

appMap = {
    "ChatOverlay": chat.router,
    "ServiceManager": selector.router,
    "CurlManager": curl.router
}

@app.get("/")
def initConnection():
    return {
        "status code": 200,
        "content": "Connection successful"
    }

def loadServices():
    services = general.readJSON(
        general.pathInfo("jsonUtils")+"services.json"
    )["Server"]

    for service in services:
        router, runLoop = serviceMap[service]
        app.include_router(
            router
        )
        if not runLoop:
            continue

        tasks.append(
            runLoop
        )

    for application in appMap:
        app.include_router(appMap[application])

    app.include_router(remoteserver.router)
    app.include_router(register.router)

@asynccontextmanager
async def lifespan(app):

    runningTasks = []

    for task in tasks:
        runningTasks.append(
            asyncio.create_task(task())
        )

    yield

    for task in runningTasks:
        task.cancel()

    await asyncio.gather(
        *runningTasks,
        return_exceptions=True
    )

app.router.lifespan_context = lifespan

def run():
    loadServices()

    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000
    )


if __name__ == "__main__":
    run()