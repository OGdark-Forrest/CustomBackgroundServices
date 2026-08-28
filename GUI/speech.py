from utils.imports import *
from utils import general

win = None

def updateParameter(key, value):
    info = general.readJSON(general.pathInfo("jsonService")+"serviceParams.json")
    params = info["SpeechPause"]
    params[key] = value
    general.writeJSON(general.pathInfo("jsonService")+"serviceParams.json", info)    

def getParameter(key):
    params = general.readJSON(general.pathInfo("jsonService")+"serviceParams.json")["SpeechPause"]
    return params[key]    

class Label(ctk.CTkLabel):
    def __init__(self, master, text, font=None):
        super().__init__(master, text=text, font=font)

    def gridWidget(self, row, column):
        self.grid(row=row, column=column, sticky="nsew", padx=(5, 5), pady=(5, 5))

class SliderFrame(ctk.CTkFrame):
    def __init__(self, master, labelText, labelTuple: tuple, sliderInfo, updateCommand, setCommand):
        super().__init__(master)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        Label(self, text=labelText).gridWidget(0, 0)

        labelContainer = ctk.CTkFrame(self)
        labelContainer.grid_columnconfigure(tuple(range(len(labelTuple))), weight=1)

        for i in range(len(labelTuple)):
            Label(labelContainer, text=labelTuple[i]).gridWidget(0, i)

        labelContainer.grid(row=1, column=0, sticky="nsew", padx=(5, 5), pady=(5, 5))

        slider = ctk.CTkSlider(self, number_of_steps=sliderInfo[0], from_=sliderInfo[1], to=sliderInfo[2], command=updateCommand)
        slider.set(setCommand())
        slider.grid(row=2, column=0, sticky="nsew", padx=(5,5), pady=(5,5))

    def gridWidget(self, row, column):
        self.grid(row=row, column=column, sticky="nsew", padx=(10, 10), pady=(10, 10))

class Window(ctk.CTk):
    def __init__(self, x=None, y=None):
        super().__init__()
        self.configure(fg_color="black")
        if x is None and y is None:
            self.geometry("500x275")
        else:
            self.geometry(f"500x275+{x}+{y-275}")
        self.overrideredirect(True)

        self.createWidgets()

    def getSensitivity(self):
        return 10 - 10*getParameter("VAD Threshold")

    def getMinSilenceDuration(self):
        return getParameter("MinSilenceDuration")

    def updateSensitivity(self, value):
        updateParameter("VAD Threshold", 1 - value/10)
        
    def updateSilenceDuration(self, value):
        updateParameter("MinSilenceDuration", value)

    def createWidgets(self):
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        SliderFrame(
            master=self,
            labelText="Enter the sensitivity:",
            labelTuple=("Better Be Human", "Probably Good Enough", "Don't Sneeze"),
            sliderInfo=(10, 0, 10),
            updateCommand=self.updateSensitivity,
            setCommand=self.getSensitivity
        ).gridWidget(0, 0)

        SliderFrame(
            master=self,
            labelText="Enter the minimum silence duration:",
            labelTuple=("Near Instant", "Avg Convo", "Turtle ahh"),
            sliderInfo=(29, 100, 3000),
            updateCommand=self.updateSilenceDuration,
            setCommand=self.getMinSilenceDuration
        ).gridWidget(1, 0)

def checkToggle():
    global win
    win.after(0, win.withdraw)
    currStatus = 0
    while True:
        if getParameter("toggleWindow") == "False":
            time.sleep(0.5)
            continue

        if currStatus == 1:
            win.after(0, win.withdraw)
            currStatus = 0
        else:
            win.geometry(f"+{getParameter("xPos")}+{getParameter("yPos")}")
            win.after(0, win.deiconify)
            win.lift()
            win.attributes("-topmost", True)
            win.after(100, lambda: win.attributes("-topmost", False))
            currStatus = 1

        updateParameter("toggleWindow", "False")

def run():
    global win
    win = Window()
    threading.Thread(target=checkToggle, daemon=True).start()

    win.mainloop()

if __name__ == "__main__":
    run()