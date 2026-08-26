from utils.imports import *
from BackgroundTasks.service import operations
import utils.general as general

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__()
        width = 150
        height = 70

        x = 1750
        screenWidth = self.winfo_screenwidth()
        baseWidth = 2496
        scaleX = screenWidth/baseWidth

        SPI_GETWORKAREA = 48
        rect = RECT()

        ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
        )

        taskbar_top = rect.bottom
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.keep_on_top()
        self.geometry(f"{width}x{height}+{int(x*scaleX)}+{taskbar_top}")

        self.player = operations.PlaybackManager()

    def createButtons(self):
        toggleSym = "⏯"
        prevSym = "⏮"
        nextSym = "⏭"

        buttonFont = ctk.CTkFont(size=25)

        overlayColor = self.cget("fg_color")

        self.toggleButton = ctk.CTkButton(
            self,
            text=toggleSym,
            width=20,
            height=40,
            fg_color=overlayColor,
            text_color="white",
            font=buttonFont,
            command=lambda: self.runAsync("toggle")
        )
        self.toggleButton.place(x=50, y=5)

        self.prevButton = ctk.CTkButton(
            self,
            text=prevSym,
            width=20,
            height=40,
            fg_color=overlayColor,
            text_color="white",
            font=buttonFont,
            command=lambda: self.runAsync("prev")
        )
        self.prevButton.place(x=0, y=5)

        self.nextButton = ctk.CTkButton(
            self,
            text=nextSym,
            width=20,
            height=40,
            fg_color=overlayColor,
            text_color="white",
            font=buttonFont,
            command=lambda: self.runAsync("next")
        )
        self.nextButton.place(x=100, y=5)

    def keep_on_top(self):
        self.attributes("-topmost", True)
        self.after(1000, self.keep_on_top)

    def runAsync(self, action):
        if action == "toggle":
            print("toggle function")
            fun = self.player.toggle
        elif action == "prev":
            fun = self.player.prevSong
        elif action == "next":
            fun = self.player.nextSong

        print("Calling action")
        asyncio.run(fun())

def run():
    overlay = Overlay()
    overlay.createButtons()
    asyncio.run(overlay.player.setManager())

    def check():
        running = general.checkRunning("SpotifyOverlay")
        if not running:
            overlay.withdraw()
        else:
            asyncio.run(overlay.player.checkPlaybackStatus("Spotify", disableNotification=True))
            overlay.deiconify()

        overlay.after(1000, check)

    check()
    overlay.mainloop()