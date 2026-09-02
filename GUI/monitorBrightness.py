from utils.imports import *

c = wmi.WMI(namespace='wmi')

def setInternalBrightness(value):
    methods = c.WmiMonitorBrightnessMethods()
    for method in methods:
        method.WmiSetBrightness(Brightness=value, Timeout=1)

def getInternalBrightness():
    return c.WmiMonitorBrightness()[0].CurrentBrightness

def setMonitorBrightness(monitor: monitorcontrol.Monitor, value):
    with monitor:
        monitor.set_luminance(value)

def getMonitorBrightness(monitor: monitorcontrol.Monitor):
    with monitor:
        return monitor.get_luminance()

class Label(ctk.CTkLabel):
    def __init__(self, master, text, font=None):
        super().__init__(master, text=text, font=font)

    def gridWidget(self, row, column, sticky):
        self.grid(row=row, column=column, sticky=sticky, padx=(5, 5), pady=(5, 5))

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="black")

        self.displays = self.detectDisplays()
        self.displayNum = len(self.displays)

        self.updateState = False

    class BrightnessFrame(ctk.CTkFrame):
        def __init__(self, master, displayObject=None):
            super().__init__(master)
            self.displayObject = displayObject

            self.createWidgets()
            self.backgroundBrightnessUpdate()

        def setBrightness(self, value):
            if self.displayObject is not None:
                setMonitorBrightness(self.displayObject, value)
            else:
                setInternalBrightness(value)

        def getBrightness(self):
            if self.displayObject is None:
                return getInternalBrightness()
            else:
                return getMonitorBrightness(self.displayObject)

        def createWidgets(self):
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure((0, 2), weight=1)

            labelContainer = ctk.CTkFrame(self)
            labelContainer.grid_columnconfigure((0, 1), weight=1)

            Label(labelContainer, "0").gridWidget(0, 0, "nsw")
            Label(labelContainer, "100").gridWidget(0, 1, "nse")

            labelContainer.grid(row=0, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))

            self.slider = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=100, command=self.setBrightness)
            self.slider.grid(self, row=1, column=0, sticky="nsew", padx=(10, 10), pady=(10, 10))

            self.currBrightness = Label(self, self.getBrightness())
            self.currBrightness.gridWidget(2, 0, "nsw")

        def backgroundBrightnessUpdate(self):
            currBrightness = self.getBrightness()
            self.slider.set(currBrightness)
            self.currBrightness.configure(text=currBrightness)
            self.after(100, self.backgroundBrightnessUpdate)

        def destroyFrame(self):
            self.destroy()

    def detectDisplays(self):
        displays = []

        internal = c.WmiMonitorBrightnessMethods()

        if internal:
            displays.append({
                "name": "Internal Display",
                "type": "internal",
                "object": None
            })

        for i, monitor in enumerate(monitorcontrol.get_monitors()[bool(internal):]):
            displays.append({
                "name": f"Monitor {i + 1}",
                "type": "external",
                "object": monitor
            })

        return displays

    def createWidgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.TabView = ctk.CTkTabview(self)

        if self.checkInternal() is False:
            for i in range(1, self.displayNum+1):
                self.TabView.add(f"Monitor {i}")
            self.TabView.set("Monitor 1")
        else:
            self.TabView.add("Internal Display")
            for i in range(1, self.displayNum):
                self.TabView.add(f"Monitor {i}")
            self.TabView.set("Internal Display")

    def 


    def checkInternal(self):
        monitors = c.WmiMonitorBrightnessMethods()
        if not monitors:
            return False
        return True

    def getDisplays(self):
        return len(monitorcontrol.get_monitors())

    def backgroundDisplayUpdate(self):
        if self.getDisplays() != self.displayNum:
            self.updateState = True

        if self.updateStatus == True:
            self.TabView.destroy()
            self.createWidgets()