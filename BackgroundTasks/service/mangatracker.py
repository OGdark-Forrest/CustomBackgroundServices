from utils.imports import *
import utils.general as general

async def run():
    mapFile = general.pathInfo("jsonService")+"map.json"
    while True:
        condition = general.checkRunning("MangaTracker")
        if not condition:
            await asyncio.sleep(1)
            continue
        d = general.readJSON(mapFile)

        for manga in d:
            urlFormat, latestChapter = d[manga]
            url = urlFormat.replace("()", str(latestChapter+1))

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    if response.url != url:
                        continue
                    d[manga] = [urlFormat, latestChapter+1]
                    general.notificationThread("New Manga Chapter added", f"{manga}: {latestChapter+1}")

            except requests.exceptions.ConnectionError:
                general.notificationThread("Domain name to be checked", f"Manga: {manga}")

            except Exception as e:
                general.notificationThread("Unknown error occured", f"{e}")
                
        general.writeJSON(mapFile, d)

        for _ in range(86400):
            if not general.checkRunning("MangaTracker"):
                break
            await asyncio.sleep(1)