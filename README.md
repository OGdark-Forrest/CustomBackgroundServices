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

pip install customtkinter fastapi "uvicorn[standard]" pyautogui PyAudio torch silero-vad psutil WMI monitorcontrol mss pillow websockets requests pydantic win11toast winsdk
```

Once installed, the service manager can be started by running main.py.

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
