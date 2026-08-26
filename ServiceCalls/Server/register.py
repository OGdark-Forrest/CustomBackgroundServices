from utils.imports import *
import utils.general as general

router = APIRouter()
jobFile = general.pathInfo("jsonAuth")+"jobs.json"
deviceFile = general.pathInfo("jsonAuth")+"devices.json"

class content(BaseModel):
    name: str
    ip: str

class Overlay(ctk.CTk):
    def __init__(self, deviceName, IP, jobID):
        super().__init__()

        self.deviceName = deviceName
        self.ip = IP
        self.jobID = jobID

        self.addJob()

        self.infoFont = ctk.CTkFont(family="consolas", size=15, weight="bold")
        self.dataFont = ctk.CTkFont(family="consolas", size=15, weight="normal")

        self.geometry("400x200")
        self.configure(fg_color="black")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.createLabels()
        self.createButtons()

    def createLabels(self):
        self.infoContainer = ctk.CTkFrame(self, fg_color="black")
        self.infoContainer.grid(row=0, column=0, sticky="nsew", padx=(10, 10))
        color = "black"

        self.infoContainer.grid_rowconfigure((0, 1), weight=1)
        self.infoContainer.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(self.infoContainer, text="Device Name: ", font=self.infoFont, fg_color=color).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self.infoContainer, text="IP Address: ", font=self.infoFont, fg_color=color).grid(row=2, column=0, sticky="w")

        ctk.CTkLabel(self.infoContainer, text=self.deviceName, font=self.dataFont, fg_color=color).grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(self.infoContainer, text=self.ip, font=self.dataFont, fg_color=color).grid(row=2, column=1, sticky="e")

    def createButtons(self):
        self.buttonContainer = ctk.CTkFrame(self)
        self.buttonContainer.grid(row=1, column=0)
        self.grid_columnconfigure((0, 1), weight=1)

        rejectButton = ctk.CTkButton(self.buttonContainer, text="Reject", fg_color="red", command=self.rejectJob)
        rejectButton.grid(row=0, column=0)

        acceptButton = ctk.CTkButton(self.buttonContainer, text="Accept", fg_color="green", command=self.admitJob)
        acceptButton.grid(row=0, column=1)

    def admitJob(self):
        jobs = general.readJSON(jobFile)
        jobs[self.jobID]["Status"] = "Accepted"
        general.writeJSON(jobFile, jobs)
        self.destroy()

    def rejectJob(self):
        jobs = general.readJSON(jobFile)
        jobs[self.jobID]["Status"] = "Rejected"
        general.writeJSON(jobFile, jobs)
        self.destroy()

    def addJob(self):
        jobs = general.readJSON(jobFile)
        jobs[self.jobID] = {
            "Status": "Pending", 
            "Device Name": self.deviceName, 
            "IP Address": self.ip
            }
        general.writeJSON(jobFile, jobs)

def run(name, ip, jobID):
    overlay = Overlay(name, ip, jobID)

    overlay.mainloop()

def registerDevice(deviceName):
    deviceID = str(uuid.uuid4())
    deviceKey = str(uuid.uuid4())

    devices = general.readJSON(deviceFile)
    devices[deviceID] = {
        "deviceName": deviceName,
        "deviceKey": deviceKey
    }

    general.writeJSON(deviceFile, devices)

    return deviceID, deviceKey

@router.post("/register/new")
def registerNew(content: content):
    jobID = str(uuid.uuid4())

    threading.Thread(
        target=run,
        args=(content.name, content.ip, jobID),
        daemon=True
    ).start()

    return {"Status": "Job Pending", "JobID": jobID}

@router.get("/register/check")
def registerCheck(jobID):
    jobs = general.readJSON(jobFile)

    if jobID not in jobs:
        return {
            "status code": 404,
            "status": "Job not found"
        }

    if jobs[jobID]["Status"] == "Rejected":
        return {
            "status code": 401,
            "status": "Access Denied"
        }
    elif jobs[jobID]["Status"] == "Pending":
        return {
            "status code": 202,
            "status": "Pending action"
            }

    deviceID, deviceKey = registerDevice(jobs[jobID]["Device Name"])

    jobs.pop(jobID)
    general.writeJSON(jobFile, jobs)

    return {
        "status code": 200,
        "status": "Succesfully Registered",
        "deviceKey": deviceKey,
        "deviceID": deviceID
        }