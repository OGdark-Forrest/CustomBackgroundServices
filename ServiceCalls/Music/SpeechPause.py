import asyncio
from utils import general
from BackgroundTasks.service.speechpause import run
logger = general.setLogger("ServiceCalls-Music-SpeechPause")

logger.info("Starting SpeechPause process")
print("Starting SpeechPause Process")
asyncio.run(run())