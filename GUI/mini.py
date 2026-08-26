from utils.imports import *
from utils import general

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

        self.overrideredirect(True)
        self.attributes("-topmost", True)

        self.dragX = 0
        self.dragY = 0

        SPI_GETWORKAREA = 48
        rect = RECT()

        ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
        )

        taskbar_top = rect.bottom

        self.geometry(f"300x50+1000+{taskbar_top}")
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.grid_rowconfigure(0, weight=0)

        self.createButtons()
        self.keep_on_top()

    def createButton(self, appName, symbol, column):
        color = self.cget("fg_color")
        font = ctk.CTkFont(size=20)
        button = ctk.CTkButton(
            self, 
            fg_color=color, 
            text=symbol, 
            width=50, 
            height=50, 
            font=font, 
            command=lambda:self.runApp(appName),
            border_width=1,
            border_color="white")
        button.grid(row=0, column=column, sticky="nsew")       

    def createButtons(self):
        color = self.cget("fg_color")
        font = ctk.CTkFont(size=20)

        ctk.CTkButton(
            self, 
            fg_color=color, 
            text="✕", width=50, 
            height=50, 
            font=font, 
            command=self.destroy,
            border_width=1,
            border_color="white"
            ).grid(row=0, column=0, sticky="nsew")
        moveButton = ctk.CTkButton(
            self, 
            fg_color=color, 
            text="↔", 
            width=50, 
            height=50, 
            font=font, 
            hover=False,
            border_width=1,
            border_color="white")
        moveButton.grid(row=0, column=1, sticky="nsew")
        moveButton.bind("<Button-1>", self.startDrag)
        moveButton.bind("<B1-Motion>", self.move)

        count = 2
        for app, symbol in [("ServiceManager", "🛠"), ("ChatOverlay", "💬"), ("CurlManager", "🌐"), ("SongMonitor", "🎵")]:
            self.createButton(app, symbol, count)
            count += 1

    def startDrag(self, event=None):
        self.dragX = event.x
        self.dragY = event.y

    def move(self, event):
        x = self.winfo_x() + event.x - self.dragX
        y = self.winfo_y() + event.y - self.dragY

        self.geometry(f"200x50+{x}+{y}")

    def keep_on_top(self):
        self.attributes("-topmost", True)
        self.after(1000, self.keep_on_top)

    def runApp(self, appName):
        response = requests.put(f"https://aetherlink.uk/{appName}Focus", headers={"key": "This is local only hahahaha"}).json()
        if response["status"] == "closed":
            subprocess.Popen(
                ["wscript.exe", general.pathInfo("vbs")+f"{appName}.vbs"],
                creationflags=subprocess.CREATE_NO_WINDOW|subprocess.CREATE_NEW_PROCESS_GROUP
            )

def run():
    overlay = Overlay()
    
    overlay.mainloop()

run()