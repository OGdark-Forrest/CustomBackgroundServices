from utils.imports import *
import utils.general as general
from .backEnd.agent import model, SummaryAgent

router = APIRouter()

windowFile = general.pathInfo("jsonUtils")+"window.json"

overlay = None

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__()

        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        width = 600
        height = 400
        self.geometry(
            f"{width}x{height}+{screenWidth - width}+{screenHeight - height}"
        )

        self.title("ChatOverlay")

        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1)
        ctk.set_window_scaling(1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.chatFont = ctk.CTkFont(family="consolas", size=14)

        self.createScroll()
        self.createControl()

        self.currChat = ""
        self.summary = SummaryAgent()

        self.protocol("WM_DELETE_WINDOW", self.onClose)

        self.checkCommands()

        self.responses = []

    def createScroll(self):
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="black")
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll._parent_canvas.configure(yscrollincrement=15)

    def createControl(self):
        self.controlFrame = ctk.CTkFrame(self)
        self.controlFrame.grid(row=1, column=0, sticky="nsew")
        self.controlFrame.grid_columnconfigure(0, weight=1)
        self.controlFrame.grid_columnconfigure(1, weight=0)
        self.controlFrame.grid_columnconfigure(2, weight=0)

        self.createEntry()
        self.createButtons()

    def createEntry(self):
        self.entry = ctk.CTkTextbox(self.controlFrame, height=45, wrap="word", font=self.chatFont)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.after(200, self.entry.focus_set)
        self.entry.bind("<Return>", self.processPrompt)
        self.entry.bind("<Shift-Return>", lambda e: self.entry.insert("insert", "\n"))

    def createButtons(self):
        self.sendButton = ctk.CTkButton(self.controlFrame, text="Send", fg_color="#287edb", width=75, command=self.processPrompt)
        self.sendButton.grid(row=0, column=1, sticky="ns")

        self.newButton = ctk.CTkButton(self.controlFrame, text="New", fg_color="#03a538", width=75, command=self.processNew)
        self.newButton.grid(row=0, column=2, sticky="ns")

    def processPrompt(self, event=None):
        prompt = self.entry.get("0.0", "end").strip()
        self.entry.delete("0.0", "end")

        self.after(0, self.showText, prompt, "USER")

        general.notificationThread("Getting your results...")

        self.currChat += f"User: {prompt}\n"
        context = self.summary.call(conversation=self.currChat)

        prompt += f"Current Conversation:{self.currChat}\nContext:{context}\n\nSpeak to me like a good friend. Don't use bold, italics, etc. Plain text output, NO EMOJIS"

        threading.Thread(
        target=self.getResponse,
        args=(prompt, ),
        daemon=True
        ).start() 

    def getResponse(self, prompt):
        content = model.get_content(prompt=prompt)

        general.notificationThread("Results received.")

        self.after(0, self.showText, content, "LLM")

        self.currChat += f"LLM: {content}\n"

    def copyAction(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    def showText(self, content, role):
        messageFrame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        messageFrame.pack(fill="x", pady=20)

        buttonFont = ctk.CTkFont(size=10)

        message = ctk.CTkLabel(
            messageFrame,
            text=content,
            wraplength=500,
            font=self.chatFont,
            justify="left",
            fg_color="#287edb" if role == "USER" else "#03a538",
            corner_radius=10,
            padx=10,
            pady=10
        )

        copyButton = ctk.CTkButton(
            messageFrame,
            text="⧉",
            fg_color="#287edb" if role == "USER" else "#03a538",
            hover=False,
            font=buttonFont,
            command=lambda:self.copyAction(content),
            width=message.cget("width")
        )
        if role == "USER":
            anchor = "ne"
        else:
            anchor = "nw"
        copyButton.pack(side="top", anchor=anchor, padx=10)

        if role == "USER":
            message.pack(side="right", padx=10)
        else:
            message.pack(side="left", padx=10)

    def save(self):
        self.summary.save(conversation=self.currChat)

    def processNew(self):
        threading.Thread(
        target=self.save,
        daemon=True
        ).start() 
        self.scroll.destroy()
        self.createScroll()
        self.currChat = ""

    def focusWindow(self):
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

        ctypes.windll.user32.SetForegroundWindow(self.winfo_id())

    def checkCommands(self):
        windows = general.readJSON(windowFile)
        info = windows["ChatOverlay"]

        if info["created"] == "True" and info["setFocus"] == "True":
            self.focusWindow()
            windows["ChatOverlay"]["setFocus"] = "False"
            general.writeJSON(windowFile, windows)
        self.after(100, self.checkCommands)

    def onClose(self):
        windows = general.readJSON(windowFile)
        windows["ChatOverlay"]["created"] = "False"
        general.writeJSON(windowFile, windows)

        self.destroy()

@router.put("/ChatOverlayFocus")
def getFocus(key: str = Header()):
    if key != "This is local only hahahaha":
        return {"status": "invalid key"}

    windows = general.readJSON(windowFile)

    if windows["ChatOverlay"]["created"] == "False":
        return {"status": "closed"}

    windows["ChatOverlay"]["setFocus"] = "True"

    general.writeJSON(windowFile, windows)

    return {"status": "setting focus"}

def run():
    global overlay
    overlay = Overlay()

    windows = general.readJSON(windowFile)
    windows["ChatOverlay"]["created"] = "True"
    general.writeJSON(windowFile, windows)

    overlay.mainloop()

if __name__ == "__main__":
    run()