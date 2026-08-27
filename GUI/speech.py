from utils.imports import *

win = None

class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="black")
        self.overrideredirect = True

    def serviceToggleFrame(self):
        toggleFrame = ctk.CTkFrame(self)
        toggleFrame.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(toggleFrame, text="SpeechPause Service Toggle: ")
        label.grid(row=0, column=0, sticky="nsw", padx=(10, 10), pady=(10, 10))

        toggleOnButton = ctk.CTkButton(toggleFrame)

    def createWidgets(self):
        self.grid_rowconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

def run():
    global win
    win = Window()

    win.mainloop()

def toggle(currStatus, xPos, yPos):
    global win
    if win is None:
        run()

    win.geometry(f"+{xPos}+{yPos}")
    
    if currStatus == 1:
        win.withdraw()
    else:
        win.deiconify()

run()