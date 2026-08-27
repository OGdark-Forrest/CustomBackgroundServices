from utils.imports import *
from utils import general

from .operations import PlaybackManager
from .SoundcoreAPI import Soundcore

general.configureLogger("stdout.log")
macaddress = "84:9D:4B:35:A7:C1"

async def connect(macaddress):
    global isConnected
    isConnected = False

    if not await checkSoundcore():
        return

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
    if isConnected:
        global isTransparency
        if isTransparency:
            Headphone.ANC("ANC Indoor")
            isTransparency = False
        else:
            Headphone.ANC("Transparency")
            isTransparency = True

def getInputDeviceIndex(portAudio):
    audio = portAudio

    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info["name"] == "Microphone Array (Qualcomm(R) A":
            return i
        
    return None

MAC = 0x849D4B35A7C1
async def checkSoundcore():
    device = await BluetoothDevice.from_bluetooth_address_async(MAC)

    if device is None:
        return False

    if device.connection_status == BluetoothConnectionStatus.CONNECTED:
       return True
    else:
        return False

async def checkConnection():
    global isConnected
    while True:
        try:
            connectedToSoundcore = await checkSoundcore()

            if not connectedToSoundcore and isConnected:
                isConnected = False
                logger.info("Headphones have been disconnected")
                general.notificationThread("Soundcore is Disconnected")

            elif connectedToSoundcore and not isConnected:
                logger.info("Headphones have been reconnected")
                await connect(macaddress)

        except Exception:
            logger.exception("checkConnection crashed")

        await asyncio.sleep(1)

def thread_target():
    asyncio.run(checkConnection())

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

    logger.debug("Attempting to connect to SoundCore")
    await connect(macaddress)

    isTransparency = False
    if isConnected:
        Headphone.ANC("ANC Indoor")

        wasPlaying = False

    threading.Thread(target=thread_target, daemon=True).start()

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

        try:
            audio = pyaudio.PyAudio()

            device_index = getInputDeviceIndex(audio)

            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )

            general.notificationThread("SpeechPause is listening...")

        except Exception:
            logger.exception("AUDIO INITIALIZATION FAILED")
            return
        
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
                    logger.debug("No Session")
                    continue
                playbackInfo = playbackManager.currSession.get_playback_info()

                if "start" in result:
                    logger.debug("Speech detected")
                    if playbackInfo.playback_status != playbackManager.PLAYING:
                        continue

                    if isConnected:
                        toggleANC()
                        logger.debug("Toggled ANC")
                    await playbackManager.toggle()
                    logger.debug("Toggled Playback")
                    wasPlaying = True

                elif "end" in result:
                    if not wasPlaying:
                        continue
                    await playbackManager.toggle()
                    toggleANC()
                    wasPlaying = False
                    logger.debug("Speech Ended")

        except Exception as e:
            logger.exception(str(e))
            terminateAudio()
            logger.warning("Terminating Audio due to Exception")