from utils.imports import *
from BackgroundTasks.service.songmodify import ModifySession
from utils import general

ctk.set_default_color_theme("dark-blue")
ctk.set_appearance_mode("dark")

windowFile = general.pathInfo("jsonUtils")+"window.json"
router = APIRouter()

app = None

class AppStart:
    def __init__(self):
        self.window = None
        self.sesh = ModifySession()
        self.scrollFrame = None
        self.selectedSong = None

    def startWindow(self):
        self.window = ctk.CTk()
        self.window.geometry("1200x600")
        self.window.title("Modify Song Restrictions")

    def createScrollFrame(self, x, y):
        scrollable_frame = ctk.CTkScrollableFrame(self.window, width=480, height=520)
        scrollable_frame.place(x=x, y=y)
        self.scrollFrame = scrollable_frame
        self.addToScroll()

    def createNameButton(self, id, songEntry, x, y):
        self.songNameFont = ctk.CTkFont(family="Consolas", size=20)

        HEIGHT = 50
        WIDTH = 680

        interval, artists, songName = songEntry
        newName = self.clipName(songName)

        songButton = ctk.CTkButton(
            master=self.scrollFrame,
            text=newName,
            fg_color=self.scrollFrame.cget("fg_color"),
            font=self.songNameFont,
            height=HEIGHT,
            width=WIDTH,
            anchor="w"
        )

        songButton.configure(command=lambda b=songButton: self.setSelectedButton(b))

        songButton.id = id
        songButton.songName = songName
        songButton.clippedName = self.clipName(songName)
        songButton.artistName = artists
        songButton.start, songButton.end = interval

        songButton.pack(pady=5)

    def modifyButtons(self, offsetx, offsety):
        self.modifyButtonFont = ctk.CTkFont(family="Consolas", size=20)
        HEIGHT = 50
        WIDTH = 240

        addButton = ctk.CTkButton(
            self.window, 
            text="Add restriction", 
            fg_color="green", 
            text_color="white",
            height=HEIGHT,
            width=WIDTH,
            font=self.modifyButtonFont,         
            command=lambda:self.checkSelected("add"))
        addButton.place(x=880+offsetx, y=200+offsety)

        removeButton = ctk.CTkButton(
            self.window, 
            text="Remove restriction", 
            fg_color="red", 
            text_color="white",
            height=HEIGHT,
            width=WIDTH,
            font=self.modifyButtonFont, 
            command=lambda:self.checkSelected("remove"))
        removeButton.place(x=880+offsetx, y=275+offsety)

        modifyButton = ctk.CTkButton(
            self.window, 
            text="Modify restriction", 
            fg_color="blue", 
            text_color="white",
            height=HEIGHT,
            width=WIDTH,
            font=self.modifyButtonFont, 
            command=lambda:self.checkSelected("modify"))
        modifyButton.place(x=880+offsetx, y=350+offsety)

    def setSelectedButton(self, button):
        if self.selectedSong:
            self.selectedSong.configure(fg_color=self.scrollFrame.cget("fg_color"))
        self.selectedSong = button
        if button:
            button.configure(fg_color="cyan")

            self.songLabel.configure(text=button.clippedName)
            self.artistLabel.configure(text=button.artistName)
            self.timeLabel.configure(text=f"{self.sesh.convertToStandard(button.start)}-{self.sesh.convertToStandard(button.end)}")
        else:
            self.songLabel.configure(text="")
            self.artistLabel.configure(text="")
            self.timeLabel.configure(text="")

    def checkSelected(self, type):
        if not self.selectedSong and type != "add":
            toast("Please select a song for action", "No restriction has been selected")
            return
        if type == "add":
            self.addRestriction()
        elif type == "remove":
            self.removeRestriction()
        elif type == "modify":
            self.modifyRestriction()

    def addRestriction(self):
        def checkSong(nameEntry, artistEntry):
            def checkTime(startEntry, endEntry):
                start, end = startEntry.get(), endEntry.get()
                response = self.sesh.checkTimes(start, end, id)
                if not response:
                    toast("Invalid times selected", f"Song Name: {songName}")
                    return
                self.sesh.logSongEntry(response, artistName, songName, id)
                toast("Restriction successfully added", f"{songName}, {response}")
                timepopup.destroy()

                popup.destroy()

                self.updateScroll()

            id, songName, artistName = self.sesh.getSongID(nameEntry.get(), artistEntry.get())

            if not id:
                toast("Song Doesn't Exist")
            else:
                toast("Song Found", f"{songName} by {artistName}")

            HEIGHT=50
            WIDTH=350

            timepopup = ctk.CTkToplevel(self.window)
            timepopup.geometry("400x300")

            timepopup.lift()
            timepopup.focus_force()

            startEntry = ctk.CTkEntry(timepopup, placeholder_text="Enter starting time [min:sec]", height=HEIGHT, width=WIDTH)
            startEntry.place(x=25, y=75)

            endEntry = ctk.CTkEntry(timepopup, placeholder_text="Enter ending time [min:sec]", height=HEIGHT, width=WIDTH)
            endEntry.place(x=25, y=150)

            submitButton = ctk.CTkButton(timepopup, text="Add", command=lambda:checkTime(startEntry, endEntry), width=100, height=HEIGHT, font=self.modifyButtonFont)
            submitButton.place(x=150, y=225)

            timepopup.mainloop()

        popup = ctk.CTkToplevel(self.window)
        popup.geometry("400x300")

        popup.lift()
        popup.focus_force()

        HEIGHT=50
        WIDTH=350

        nameEntry = ctk.CTkEntry(popup, placeholder_text="Enter song name here (doesn't need to be perfect)", height=HEIGHT, width=WIDTH)
        nameEntry.place(x=25, y=75)
        artistEntry = ctk.CTkEntry(popup, placeholder_text="Enter artist name here", height=HEIGHT, width=WIDTH)
        artistEntry.place(x=25, y=150)

        searchButton = ctk.CTkButton(popup, text="Verify Song", fg_color="green", command=lambda:checkSong(nameEntry, artistEntry), height=HEIGHT, width=100)
        searchButton.place(x=150, y=225)

        popup.mainloop()

        return popup

    def removeRestriction(self):
        button = self.selectedSong
        self.sesh.removeEntry(button.id)
        toast("Song Restriction succesfully removed")
        self.updateScroll()
        self.setSelectedButton(None)

    def modifyRestriction(self):
        def checkTime(startEntry, endEntry):
            start, end = startEntry.get(), endEntry.get()
            response = self.sesh.checkTimes(start, end, id)
            if not response:
                toast("Invalid times selected", f"Song Name: {songName}")
                return
            self.sesh.logSongEntry(response, artistName, songName, id)
            toast("Restriction successfully modified", f"{songName}, {response}")
            popup.destroy()
            self.updateScroll()

        id, songName, artistName = self.selectedSong.id, self.selectedSong.songName, self.selectedSong.artistName

        popup = ctk.CTkToplevel(self.window)
        popup.geometry("400x300")

        popup.lift()
        popup.focus_force()

        HEIGHT=50
        WIDTH=350

        startEntry = ctk.CTkEntry(popup, placeholder_text="Enter starting time [min:sec]", height=HEIGHT, width=WIDTH)
        startEntry.place(x=25, y=75)

        endEntry = ctk.CTkEntry(popup, placeholder_text="Enter ending time [min:sec]", height=HEIGHT, width=WIDTH)
        endEntry.place(x=25, y=150)

        submitButton = ctk.CTkButton(popup, text="Modify", command=lambda:checkTime(startEntry, endEntry))
        submitButton.place(x=150, y=225)

        popup.mainloop()

        return popup

    def addToScroll(self):
        self.sesh.getSongs()
        x = 10
        y = 10
        for id in self.sesh.songData:
            self.createNameButton(id, self.sesh.songData[id], x, y)
            y += 50

    def updateScroll(self):
        self.scrollFrame.destroy()
        self.previewFrame.destroy()
        self.selectedSong = None
        self.createScrollFrame(40, 40)
        self.createPreviewFrame()

    def createPreviewFrame(self):
        self.previewFont = ctk.CTkFont(family="Consolas", size=15)

        self.previewFrame = ctk.CTkFrame(self.window, width=600, height=260)
        self.previewFrame.place(x=580, y=40)

        color = self.previewFrame.cget("fg_color")

        ctk.CTkLabel(self.previewFrame, text="Song Name: ", font=self.previewFont, fg_color=color).place(x=20, y=60)
        ctk.CTkLabel(self.previewFrame, text="Artist Name: ", font=self.previewFont, fg_color=color).place(x=20, y=120)
        ctk.CTkLabel(self.previewFrame, text="Time Interval: ", font=self.previewFont, fg_color=color).place(x=20, y=180)

        self.songLabel = ctk.CTkLabel(self.previewFrame, text="", font=self.previewFont, fg_color=color)
        self.songLabel.place(x=200, y=60)
        self.artistLabel = ctk.CTkLabel(self.previewFrame, text="", font=self.previewFont, fg_color=color)
        self.artistLabel.place(x=200, y=120)
        self.timeLabel = ctk.CTkLabel(self.previewFrame, text="", font=self.previewFont, fg_color=color)
        self.timeLabel.place(x=200, y=180)

    def clipName(self, songName):
        newName = ""
        for ch in songName:
            if ch == "(":
                break
            newName += ch
        return newName

    def mainloop(self):
        self.window.mainloop()

    def focusWindow(self):
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

        ctypes.windll.user32.SetForegroundWindow(self.winfo_id())

    def checkCommands(self):
        windows = general.readJSON(windowFile)
        info = windows["SongMonitor"]

        if info["created"] == "True" and info["setFocus"] == "True":
            self.focusWindow()
            windows["SongMonitor"]["setFocus"] = "False"
            general.writeJSON(windowFile, windows)
        self.after(100, self.checkCommands)

    def onClose(self):
        windows = general.readJSON(windowFile)
        windows["SongMonitor"]["created"] = "False"
        general.writeJSON(windowFile, windows)

        self.destroy()


def run():
    app = AppStart()
    app.startWindow()
    app.createScrollFrame(40, 40)
    app.createPreviewFrame()
    app.modifyButtons(-175, 150)

    windows = general.readJSON(windowFile)
    windows["SongMonitor"]["created"] = "True"
    general.writeJSON(windowFile, windows)

    app.mainloop()

if __name__ == "__main__":
    run()