from utils.imports import *
import utils.general as general

windowFile = general.pathInfo("jsonUtils")+"window.json"

router = APIRouter()

app = None

def killAllProcesses():
    subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"])
    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"])

class Selector(ctk.CTk):
    def __init__(self):
        super().__init__()

        baseWidth = 2496
        baseHeight = 1663

        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()

        self.configure(fg_color="black")

        self.scaleX = screenWidth/baseWidth
        self.scaleY = screenHeight/baseHeight

        width = int(1200*self.scaleX)
        height = int(720*self.scaleY)

        self.geometry(f"{width}x{height}")
        self.title("Service Manager")

        self.serviceFile = general.pathInfo("jsonUtils")+"services.json"

        self.serviceInfo = general.readJSON(self.serviceFile)

        self.serviceGroup = {}

        self.protocol("WM_DELETE_WINDOW", self.onClose)

        self.checkCommands()

    def place(self, widget, x, y):
        widget.place(x=x*self.scaleX, y=y*self.scaleY)

    def reverseMap(self):
        for group in self.serviceInfo:
            for service in self.serviceInfo[group]:
                self.serviceGroup[service] = group

#==================================================================================================================================================================================
#WIDGET CREATION
#==================================================================================================================================================================================

    def createTabs(self):
        self.tabFont = ctk.CTkFont("Consolas", 20)

        self.tabView = ctk.CTkTabview(
            self,
            width=725*self.scaleX,
            height=660*self.scaleY,
            segmented_button_selected_color="#e31b1b")
        self.tabView.configure(command=self.fillTab)
        self.place(self.tabView, 25, 25)

        self.tabView.add("Running")
        for tabGroup in self.serviceInfo:
            self.tabView.add(tabGroup)

        self.tabView.set("Running")

    def createPreviewFrame(self):
        labelFont = ctk.CTkFont("Consolas", 12)

        self.previewFrame = ctk.CTkFrame(
            self,
            width=400*self.scaleX,
            height=635*self.scaleY
        )
        self.place(self.previewFrame, 775, 50)

        self.place(ctk.CTkLabel(
            self.previewFrame,
            text="Service name:",
            font=labelFont
        ), 25, 20)

        self.nameLabel = ctk.CTkTextbox(
            self.previewFrame,
            font=labelFont,
            fg_color="black",
            width=350*self.scaleX,
            height=40
        )
        self.place(self.nameLabel, 25, 60)

        self.place(ctk.CTkLabel(
            self.previewFrame,
            text="Service Description:",
            font=labelFont
        ), 25, 120)

        self.descriptionBox = ctk.CTkTextbox(
            self.previewFrame,
            width=350*self.scaleX,
            height=400*self.scaleY,
            wrap="word",
            fg_color="black"
        )
        self.place(self.descriptionBox, 25, 180)

    def createScroll(self, masterTab, serviceList):
        scrollFrame = ctk.CTkScrollableFrame(
            masterTab,
            width=850*self.scaleX,
            height=420*self.scaleY
        )
        self.place(scrollFrame, 50, 50)

        forceStopButton = ctk.CTkButton(masterTab, text="Force Shutdown", fg_color="#e31b1b", command=self.forceShutDown)
        self.place(forceStopButton, 50, 5)

        if self.activeTab == "Running":
            clearAllButton = ctk.CTkButton(masterTab, text="Suspend all services", fg_color="#e31b1b", command=self.clearRunning)
            self.place(clearAllButton, 500, 5)

        if self.activeTab == "Server":
            clearServerButton = ctk.CTkButton(masterTab, text="Suspend Server services", fg_color="#e31b1b", command=self.clearServer)
            self.place(clearServerButton, 500, 5)

            self.stopServerButton = ctk.CTkButton(masterTab, text="Stop Server", fg_color="#e31b1b", command=self.stopServer)
            self.place(self.stopServerButton, 500, 50)

            self.startServerButton = ctk.CTkButton(masterTab, text="Start Server", fg_color="green", command=self.startServer)

        if not serviceList:
            noneLabel = ctk.CTkLabel(
                scrollFrame,
                width=200*self.scaleX,
                text="No Currently Running Services"
            )
            noneLabel.pack()
            return

        for service in serviceList:
            self.createCheckBox(scrollFrame, service)

    def createCheckBox(self, masterScrollFrame, service):
        if self.serviceInfo[self.serviceGroup[service]][service]["running"] == "True":
            check_var = ctk.StringVar(value="on")
        else:
            check_var = ctk.StringVar(value="off")
        checkBox = ctk.CTkCheckBox(
            masterScrollFrame,
            text=service,
            command=lambda:self.checkboxConfirmation(service, check_var.get()),
            variable=check_var,
            onvalue="on",
            offvalue="off",
            fg_color="#e31b1b"
        )
        checkBox.pack(pady=10, padx=20, anchor="w")

        checkBox.bind("<Enter>", lambda e: self.hoverCheck(e, service))
        checkBox.bind("<Leave>", lambda e: self.leaveCheck(e))

#==================================================================================================================================================================================
#WIDGET UPDATION
#==================================================================================================================================================================================

    def updateTab(self):
        self.clearTab()
        self.fillTab()

    def clearTab(self):
        tab = self.tabView.tab(self.activeTab)

        for widget in tab.winfo_children():
            widget.destroy()

    def updateTextbox(self, textbox, content):
        textbox.delete("1.0", "end")
        textbox.insert("end", content)

    def clearPreview(self):
        self.updateDescription("")
        self.nameLabel.configure(text="")

    def fillTab(self):
        self.serviceInfo = general.readJSON(self.serviceFile)
        self.reverseMap()
        self.activeTab = self.tabView._current_name

        if self.activeTab == "Running":
            serviceList = self.getCurrentRunning()
        else:
            serviceList = [service for service in self.serviceInfo[self.activeTab]]

        self.createScroll(self.tabView.tab(self.activeTab), serviceList)

#==================================================================================================================================================================================
#WIDGET ACTIONS
#==================================================================================================================================================================================

    def getCurrentRunning(self):
        self.runningServices = []

        for group in self.serviceInfo:
            services = self.serviceInfo[group]
            for service in services:
                serviceData = self.serviceInfo[group][service]
                if serviceData["running"] == "True":
                    self.runningServices.append(service)

        return self.runningServices

    def clearRunning(self):
        self.getCurrentRunning()
        for service in self.runningServices:
            if service == "RemoteService":
                continue
            self.serviceInfo[self.serviceGroup[service]][service]["running"] = "False"

        general.writeJSON(general.pathInfo("jsonUtils")+"services.json", self.serviceInfo)

        general.notificationThread("All services have been stopped")
        self.updateTab()

    def clearServer(self):
        for service in self.serviceInfo["Server"]:
            if service == "RemoteService":
                continue
            self.serviceInfo["Server"][service]["running"] = "False"
            general.writeJSON(general.pathInfo("jsonUtils")+"services.json", self.serviceInfo)

        general.notificationThread("All services in Server have been stopped")
        self.updateTab()

    def stopServer(self):
        self.stopServerButton.place_forget()
        self.place(self.startServerButton, 500, 40)
        info = general.readJSON(general.pathInfo("jsonUtils")+"/status.json")
        info["serverStatus"] = "1"
        general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

    def startServer(self):
        self.startServerButton.place_forget()
        self.place(self.stopServerButton, 500, 40)
        info = general.readJSON(general.pathInfo("jsonUtils")+"/status.json")
        info["serverStatus"] = "2"
        general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

    def checkboxConfirmation(self, service, status):
        if status == "on":
            try:
                self.serviceInfo[self.serviceGroup[service]][service]["running"] = "True"
                general.writeJSON(self.serviceFile, self.serviceInfo)
                general.notificationThread("Service is running...", f"{service}")
            except Exception as e:
                general.notificationThread(str(e))
        else:
            try:
                self.serviceInfo[self.serviceGroup[service]][service]["running"] = "False"
                general.writeJSON(self.serviceFile, self.serviceInfo)
                general.notificationThread("Service has been stopped.", f"{service}")
            except Exception as e:
                raise e
        self.updateTab()

    def hoverCheck(self, event, service):
        self.updateTextbox(self.nameLabel, service)

        description = self.serviceInfo[self.serviceGroup[service]][service]["description"]
        self.updateTextbox(self.descriptionBox, description)

    def leaveCheck(self, event):
        self.updateTextbox(self.nameLabel, "")
        self.updateTextbox(self.descriptionBox, "")

    def focusWindow(self):
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

        ctypes.windll.user32.SetForegroundWindow(self.winfo_id())

    def checkCommands(self):
        windows = general.readJSON(windowFile)

        if windows["ServiceManager"]["created"] == "True" and windows["ServiceManager"]["setFocus"] == "True":
            self.focusWindow()
            windows["ServiceManager"]["setFocus"] = "False"
            general.writeJSON(windowFile, windows)
        self.after(100, self.checkCommands)

    def onClose(self):
        windows = general.readJSON(windowFile)
        windows["ServiceManager"]["created"] = "False"
        general.writeJSON(windowFile, windows)

        self.destroy()

    def forceShutDown(self):
        info = general.readJSON(general.pathInfo("jsonUtils")+"status.json")
        info["boot"] = "0"
        general.writeJSON(general.pathInfo("jsonUtils")+"status.json", info)

        killAllProcesses()

        servicePID = general.readJSON(general.pathInfo("jsonUtils")+"serviceProcesses.json")
        for service in servicePID:
            servicePID[service] = "NONE"
        general.writeJSON(general.pathInfo("jsonUtils")+"serviceProcesses.json", servicePID)

@router.put("/ServiceManagerFocus")
def getFocus(key: str = Header()):
    if key != "This is local only hahahaha":
        return {"status": "invalid key"}

    windows = general.readJSON(windowFile)

    if windows["ServiceManager"]["created"] == "False":
        return {"status": "closed"}

    windows["ServiceManager"]["setFocus"] = "True"

    general.writeJSON(windowFile, windows)

    return {"status": "setting focus"}

def run():
    global app
    app = Selector()
    app.createTabs()
    app.fillTab()
    app.createPreviewFrame()

    windows = general.readJSON(windowFile)
    windows["ServiceManager"]["created"] = "True"
    general.writeJSON(windowFile, windows)

    app.mainloop()