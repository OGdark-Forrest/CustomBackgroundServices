# Custom Background Services

## The Journey:

### The Reason:
While working and studying, I faced many small inconveniences which I thought could be solved by writing Python scripts.

### The Progression:
It started as a few files which automatically skipped over set intervals for particular songs when detected.
As the number of services I needed increased, I decided to make a unified background service manager, which helped me toggle and
manage different services.

## The Audience:
This service manager works with mainly windows APIs, like:
```python
from win11toast import toast
from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus
)
from winsdk.windows.devices.bluetooth import (
    BluetoothDevice,
    BluetoothConnectionStatus,
)
```
In case of other OS like Mac or Linux being used, these APIs can be replaced in the respective classes. I've tried to include as 
much abstraction and interfaces as possible to reduce dependency on lower level workings.

## The Usage:
Using the following command, clone the repo locally:
```python
git clone https://github.com/OGdark-Forrest/CustomBackgroundServices.git
```

After cloning, I recommend creating a virtual environment (venv) with Python 3.12 and using a pip install for the libraries being imported.

```python
py -3.12 -m venv .venv
.venv/Scripts/Activate.ps1 (for Powershell)
.venv/Scripts/Activate.bat (for Command Prompt)
pip install customtkinter fastapi "uvicorn[standard]" pyautogui PyAudio torch silero-vad psutil WMI monitorcontrol mss pillow websockets requests pydantic win11toast winsdk
```

Once installed, the service manager can be started by activating the virtual environment and running main.py.

### For running remote services:
This rmeote system is authenticated, with the server (laptop) providing the deviceID and deviceKey to the client.
For every request these two are authenticated in the header.

**Steps for Authentication**:
1. Send a request with device name and IP address to your server's address followed by `/register/new` which gives a jobID.
2. Send another request to `/register/check` giving your jobID, which returns the deviceID and deviceKey, which need to be securely stored.
3. I recommend creating some environment variable or storing it in a file locally instead of hardcoding any values.

## Potential Problems + Solutions:
In case the service manager window can't start, the following function can be added and run in Terminal to terminate all python 
processes:
```
function terminate {
    cd <path to main directory>
    . .\.venv\Scripts\Activate.ps1 (activate the venv)
    taskkill /F /IM python.exe /T
    taskkill /F /IM pythonw.exe /T
    python -m utils.reset
}
```
Check this resource for more help -> [How To Add Functions in Powershell](https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/09-functions?view=powershell-7.6)

This function terminates all python processes.

## Available Services:
### Local Services (Non-Server):
**`AutoPause`**: 
Automatically pauses and resumes Spotify music when other media is detected playing.

**`IntervalSkipper`**: 
Automatically skips over certain songs over particular intervals.
In order to add songs or manage time intervals, run the VBS file `VBS/SongMonitor.vbs` or create and run a shortcut for the same.

**`SpotifyOverlay`**:
Minimal media overlay just for controlling spotify (ALWAYS stays on top of taskbar if service is on)

**`SpeechPause`**:
Automatically pauses media if human speech is detected.
(I made some additional functionality of turning my headphone's ANC on and off accordingly, only works for Anker SoundCore Q30)
In order to change the sensitivity, run the VBS file `VBS/SpeechPause.vbs` or create and run a shortcut for the same.

**`Curl Manager`**:
Makes adding fields/urls/header/etc. easy for cURLs.
In order to use, run the VBS file `VBS/CurlManager.vbs` or create and run a shortcut for the same.

**`Chat Overlay`**:
Opens an overlay window useful for chatting with an AI LLM.
(Must provide the AI model LLM information and API_KEY environment variable in `GUI/backEnd/model.py`)
In order to use, run the VBS file `VBS/ChatOverlay.vbs`

### Remote Services:
**`Remote Player`**:
Remotely controls laptop media.

**`Remote Notes`**:
Modifies and gets project notes.
Works with a `SharedNotes` directory in `Documents`. File path may be changed in `BackgroundTasks/server/remotenote.py`.

**`Remote Start`**:
Remotely starting apps/services.
To change, remove or add modes, please check `utils/jsonFiles/service/siteApps.json`.

**`Remote Service`**:
Remotely toggling services on and off.

