from utils.imports import *
from utils import general

DEVICE_ID = os.getenv("deviceID")
DEVICE_KEY = os.getenv("deviceKey")

windowFile = general.pathInfo("jsonUtils")+"window.json"
router = APIRouter()

curl = None

class curlCommand:
    def __init__(self):
        self.url = ""
        self.requestType = "GET"
        self.params = None
        self.headers = None
        self.body = None

    def getResponse(self, func, data=None):
        response = func(self.url, params=self.params, headers=self.headers, json=data)

        return response.json()

    def runCommand(self):
        response = None
        if self.requestType == "GET":
            response = self.getResponse(requests.get)
        elif self.requestType == "PUT":
            response = self.getResponse(requests.put, self.body)
        elif self.requestType == "POST":
            response = self.getResponse(requests.post, self.body)

        return response

class curlWindow(ctk.CTk):
    def __init__(self, fg_color = None):
        super().__init__(fg_color)

        self.geometry("1200x500")
        self.title("cURL Manager")

        self.grid_rowconfigure((0, 2), weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.font = ctk.CTkFont(family="consolas", size=15)

        self.curl = curlCommand()
        self.curl.headers = {}
        self.curl.body = {}
        self.curl.params = {}

        self.createBaseFrame()
        self.createDataFrame()

        ctk.CTkButton(
            self,
            text="Run cURL",
            fg_color="#e31b1b",
            height=50,
            command=self.runCURL
        ).grid(row=2, column=0, padx=(10, 10), pady=(10, 10))

        self.protocol("WM_DELETE_WINDOW", self.onClose)

        self.checkCommands()

    def runCURL(self):
        self.curl.url = self.url.get()

        output = OutputPopup(self.curl.runCommand())
        output.mainloop()

    class ScrollableFrame(ctk.CTkScrollableFrame):
        def __init__(self, master, column):
            super().__init__(master)
            if column == 0:
                self.items = master.master.curl.headers
                self.type = "header"
            elif column == 1:
                self.items = master.master.curl.body
                self.type = "body"
            else:
                self.items = master.master.curl.params
                self.type = "query"

            self.grid(row=1, column=column, sticky="nsew", padx=(20, 10), pady=(20, 20))

            self.populateSelection()

        def populateSelection(self):
            for key in self.items:
                if key == "deviceID" or key == "deviceKey":
                    value = 36*"*"
                else:
                    value = self.items[key]
                self.createItemFrame(key, value)

        def createItemFrame(self, key, value):
            frame = ctk.CTkFrame(
                self,
                fg_color="#353535"
            )
            frame.pack(fill="x", padx=(5, 5), pady=(5, 5))
            frame.grid_rowconfigure((0, 1), weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=0)

            keyLabel = ctk.CTkLabel(
                frame,
                text=key,
                text_color="#e31b1b",
                height=30
            )
            keyLabel.grid(row=0, column=0, sticky="w", padx=(5, 5), pady=(10, 10))

            ctk.CTkLabel(
                frame,
                text=value,
                text_color="#e31b1b",
                height=30
            ).grid(row=1, column=0, sticky="w", padx=(5, 5), pady=(10, 10))

            ctk.CTkButton(
                frame,
                text="🗑",
                width=10,
                fg_color="#e31b1b",
                command=lambda:self.removeItem(keyLabel.cget("text"))
            ).grid(row=0, column=1, sticky="w", padx=(5, 5), pady=(10, 10))

        def removeItem(self, key):
            self.items.pop(key)
            self.refreshScroll()

        def destroyChildren(self):
            for widget in self.winfo_children():
                widget.destroy()

        def refreshScroll(self):
            self.destroyChildren()
            self.populateSelection()

    def createBaseFrame(self):
        self.baseFrame = ctk.CTkFrame(
            self,
            height=60,
            fg_color="black"
        )
        self.baseFrame.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))
        self.baseFrame.grid_columnconfigure((0, 1), weight=0)
        self.baseFrame.grid_columnconfigure(2, weight=1)

        optionVar = ctk.StringVar(value="GET")
        self.requestMenu = ctk.CTkOptionMenu(
            self.baseFrame,
            dropdown_hover_color="#e31b1b",
            fg_color="#e31b1b",
            width=75,
            values=["GET", "PUT", "POST"],
            variable=optionVar,
            font=self.font,
            command=self.changeRequestType
        )
        self.requestMenu.grid(row=0, column=0, padx=(20, 20))

        ctk.CTkLabel(
            self.baseFrame,
            text="URL Endpoint:",
            text_color="#e31b1b",
            height=40,
            width=50,
            fg_color="black",
            font=self.font
        ).grid(row=0, column=1, padx=(20, 10))

        self.url = ctk.CTkEntry(
            self.baseFrame,
            height=40,
            fg_color="#4d4d4d",
            font=self.font
        )
        self.url.insert(0, "https://")
        self.url.grid(row=0, column=2, padx=10, sticky="nsew")

    def changeRequestType(self, event=None):
        self.curl.requestType = self.requestMenu.get()

    def createDataFrame(self):
        self.dataFrame = ctk.CTkFrame(
            self,
            height=60,
            fg_color="black"
        )
        self.dataFrame.grid(row=1, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))
        self.dataFrame.grid_columnconfigure((0, 1, 2), weight=1)
        self.dataFrame.grid_rowconfigure(0, weight=0)
        self.dataFrame.grid_rowconfigure(1, weight=1)

        self.headerFrame = self.ScrollableFrame(self.dataFrame, 0)
        self.bodyFrame = self.ScrollableFrame(self.dataFrame, 1)
        self.queryFrame = self.ScrollableFrame(self.dataFrame, 2)

        self.createInfoFrame(0, "Header", command=lambda:self.addPopup(self.headerFrame))
        self.createInfoFrame(1, "Body", command=lambda:self.addPopup(self.bodyFrame))
        self.createInfoFrame(2, "Query", command=lambda:self.addPopup(self.queryFrame))

    def createInfoFrame(self, column, text, command=None):
        frame = ctk.CTkFrame(
            self.dataFrame,
            height=50
        )
        frame.grid(row=0, column=column, sticky="nsew", padx=(20, 10), pady=(20, 20))
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            frame,
            text=f"{text}:",
            text_color="#e31b1b",
            height=40,
            width=50,
            font=self.font
        ).grid(row=0, column=0, padx=(20, 10), sticky="w")

        ctk.CTkButton(
            frame,
            text=f"Add {text}:",
            fg_color="#e31b1b",
            width=100,
            command=command
        ).grid(row=0, column=1, sticky="e", padx=(20, 10), pady=(20, 20))

    def addPopup(self, scrollFrame: ScrollableFrame):
        popup = ctk.CTk(fg_color="black")
        popup.geometry("500x200")
        popup.grid_rowconfigure((0, 1), weight=1)
        popup.grid_rowconfigure(2, weight=0)
        popup.grid_columnconfigure(0, weight=1)

        keyEntry = self.EntryFrame(popup, 0, "Key")
        keyEntry.after(100, keyEntry.focus_set)

        valueEntry = self.EntryFrame(popup, 1, "Value")

        valueEntry.bind("<Return>", lambda event:self.addItem(scrollFrame, keyEntry.get(), valueEntry.get(), popup))
        keyEntry.bind("<Return>", lambda event:self.addItem(scrollFrame, keyEntry.get(), valueEntry.get(), popup))

        ctk.CTkButton(
            popup,
            text="Add entry",
            fg_color="#e31b1b",
            height=50,
            command=lambda:self.addItem(scrollFrame, keyEntry.get(), valueEntry.get(), popup)
        ).grid(row=2, column=0, sticky="ns", padx=(10, 10), pady=(10, 10))

        popup.mainloop()

    def EntryFrame(self, popup, row, text):
        frame = ctk.CTkFrame(
            popup
        )
        frame.grid(row=row, column=0, sticky="nsew", padx=(15, 15), pady=(15, 15))
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text=f"Enter {text}:"
        ).grid(row=0, column=0, sticky="nse", padx=(10, 10), pady=(5, 5))

        entry = ctk.CTkEntry(
            frame,
            font=self.font
        )
        entry.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=(5, 5))

        return entry

    def addItem(self, frameObject: ScrollableFrame, key, value, popup, event=None):
        if frameObject.type == "header":
            d = self.curl.headers
        elif frameObject.type == "body":
            d = self.curl.body
        else:
            d = self.curl.params

        if key == "deviceID":
            d[key] = DEVICE_ID
        elif key == "deviceKey":
            d[key] = DEVICE_KEY
        else:
            d[key] = value   

        frameObject.refreshScroll()
        popup.destroy()

    def focusWindow(self):
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

        ctypes.windll.user32.SetForegroundWindow(self.winfo_id())

    def checkCommands(self):
        windows = general.readJSON(windowFile)
        info = windows["CurlManager"]

        if info["created"] == "True" and info["setFocus"] == "True":
            self.focusWindow()
            windows["CurlManager"]["setFocus"] = "False"
            general.writeJSON(windowFile, windows)
        self.after(100, self.checkCommands)

    def onClose(self):
        windows = general.readJSON(windowFile)
        windows["CurlManager"]["created"] = "False"
        general.writeJSON(windowFile, windows)

        self.destroy()

class OutputPopup(ctk.CTk):
    def __init__(self, text):
        super().__init__()
        self.grid_columnconfigure(0, weight=1)

        font = ctk.CTkFont(family="consolas", size=20)
        
        content = ctk.CTkTextbox(
            self,
            text_color="#e31b1b",
            font=font
        )
        content.grid(row=0, column=0, sticky="nsew")

        content.insert("0.0", text)

@router.put("/CurlManagerFocus")
def getFocus(key: str = Header()):
    if key != "This is local only hahahaha":
        return {"status": "invalid key"}

    windows = general.readJSON(windowFile)

    if windows["CurlManager"]["created"] == "False":
        return {"status": "closed"}

    windows["CurlManager"]["setFocus"] = "True"

    general.writeJSON(windowFile, windows)

    return {"status": "setting focus"}

def run():
    curl = curlWindow("black")

    windows = general.readJSON(windowFile)
    windows["CurlManager"]["created"] = "True"
    general.writeJSON(windowFile, windows)

    curl.mainloop()

if __name__ == "__main__":
    run()