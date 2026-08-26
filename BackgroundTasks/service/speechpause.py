from utils.imports import *
from utils import general

from .operations import PlaybackManager
from .SoundcoreAPI import Soundcore

general.configureLogger("stdout.log")

def connect(macaddress):
    global isConnected
    isConnected = False
    def tryConnect():
        global Headphone
        global isConnected, Headphone
        try:
            Headphone = Soundcore(macaddress)
            if Headphone.Port is not None:
                Headphone.connect()
                isConnected = True
        except Exception as e:
            isConnected = False
            logger.exception(str(e))
            return

    tryConnect()
    if isConnected == False:
        general.notificationThread("Cannot connect to SoundCore")
        logger.info("Cannot connect to SoundCore")
        return
    
    tryConnect()

    logger.info("Connected to Soundcore")
    general.notificationThread("Connected to SoundCore")

def toggleANC():
    try:
        global isTransparency
        if isTransparency:
            Headphone.ANC("ANC Indoor")
            isTransparency = False
        else:
            Headphone.ANC("Transparency")
            isTransparency = True
    except:
        return

def getInputDeviceIndex():
    audio = pyaudio.PyAudio()

    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["name"] == "Microphone Array (Qualcomm(R) A":
            return i

    return None

async def run():
    global logger
    logger = general.setLogger("speechpause.py")
    def terminateAudio():
        nonlocal stream, audio
        stream.stop_stream()
        stream.close()
        audio.terminate()

        stream = None
        audio = None

    global isTransparency
    model = load_silero_vad()
    logger.debug("Loaded Silero VAD Model")

    vad = VADIterator(
        model,
        sampling_rate=16000,
        threshold=0.2,
        min_silence_duration_ms=1000,
        speech_pad_ms=100
    )
    logger.debug("Created VAD Iterator")
    stream = None
    audio = None

    macaddress = "84:9D:4B:35:A7:C1"
    isTransparency = False

    logger.debug("Attempting to connect to SoundCore")
    connect(macaddress)

    while True:
        condition = general.checkRunning("SpeechPause")
        if not condition:
            if stream and audio:
                terminateAudio()
                logger.info("Terminating Audio, service switched off")
            await asyncio.sleep(1)
            continue
        
        playbackManager = PlaybackManager()
        await playbackManager.setManager()

        RATE = 16000
        CHUNK = 512

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            input=True,
            input_device_index=getInputDeviceIndex(),
            frames_per_buffer=CHUNK
        )

        general.notificationThread("SpeechPause is listening...")
        wasPlaying = False
        try:
            while True:
                if not general.checkRunning("SpeechPause"):
                    logger.info("Service has been turned off")
                    break
                data = stream.read(CHUNK, exception_on_overflow=False)

                samples = torch.frombuffer(
                    bytearray(data),
                    dtype=torch.float32
                )

                result = vad(samples, return_seconds=False)

                if not result:
                    continue

                await playbackManager.checkPlaybackStatus()
                if playbackManager.currSession is None:
                    continue
                playbackInfo = playbackManager.currSession.get_playback_info()

                if "start" in result:
                    logger.info("Speech detected")
                    if playbackInfo.playback_status != playbackManager.PLAYING:
                        continue

                    if isConnected:
                        toggleANC()
                        logger.info("Toggled ANC")
                    await playbackManager.toggle()
                    logger.info("Toggled Playback")
                    wasPlaying = True

                elif "end" in result:
                    if not wasPlaying:
                        continue
                    await playbackManager.toggle()
                    toggleANC()
                    wasPlaying = False
                    logger.info("Speech Ended")

        except Exception as e:
            logger.exception(str(e))
            terminateAudio()
            logger.info("Terminating Audio due to Exception")