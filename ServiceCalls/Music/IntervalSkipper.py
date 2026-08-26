from BackgroundTasks.service import monitor
import asyncio

asyncio.run(monitor.run())