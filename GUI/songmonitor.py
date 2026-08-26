from utils.imports import *
from utils import general
from BackgroundTasks.service.songmodify import ModifySession

songFile = general.pathInfo("jsonService")+"songTimes.json"
font = None

def insertText(textbox, content):
    textbox.insert("0.0", content)

class SongMonitor(ctk.CTk):

    class ScrollFrame(ctk.CTkScrollableFrame):
        def __init__(self, master):
            super().__init__(master=master)
            self.preview = master.preview
            self.selected = None

            self.grid(row=0, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.grid_columnconfigure((0, 1), weight=1)

            self.populateScroll()

        def populateScroll(self):
            currRow = 0
            songTimes = general.readJSON(songFile)

            for songID in songTimes:
                songEntry = songTimes[songID]
                song, artist = songEntry[2], ", ".join(songEntry[1])
                self.createSongItem(songID, song, artist, currRow)

                currRow += 1

        def createSongItem(self, songID, song, artist, rowNum):
            pairFrame = ctk.CTkFrame(
                self,
                fg_color="#535353"
            )
            pairFrame.songID = songID
            pairFrame.grid_columnconfigure((0, 1), weight=1)
            pairFrame.grid_columnconfigure(2, weight=0)
            pairFrame.grid_rowconfigure(0, weight=1)

            songName = ctk.CTkTextbox(
                pairFrame,
                height=50,
                font=font,
                fg_color="#535353",
                text_color="white",
                wrap="word"
            )
            songName.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="w")
            insertText(songName, song)

            artistName = ctk.CTkTextbox(
                pairFrame,
                height=50,
                font=font,
                fg_color="#535353",
                text_color="white",
                wrap="word"
            )
            artistName.grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="e")
            insertText(artistName, artist)

            pairFrame.grid(row=rowNum, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

            state = "normal"
            fg_color = "#f5a22d"
            disabledColor = "#800101"
            
            ctk.CTkButton(
                pairFrame,
                height=50,
                width=75,
                text="Select",
                fg_color=fg_color,
                font=font,
                text_color="white",
                text_color_disabled=disabledColor,
                state=state,
                command=lambda:self.selectSongItem(pairFrame)
            ).grid(row=0, column=2, padx=(20, 5), pady=(5, 5))

        def selectSongItem(self, pairFrame):
            if self.selected:
                for widget in self.selected.winfo_children():
                    if isinstance(widget, ctk.CTkButton):
                        widget.configure(state="normal", text="Select")
                        continue
                    widget.configure(fg_color="#535353")
                self.selected.configure(fg_color="#535353")
            for widget in pairFrame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state="disabled", text="Selected")
                widget.configure(fg_color="#f5a22d")
            pairFrame.configure(fg_color="#f5a22d")

            self.selected = pairFrame
            self.preview.songID = pairFrame.songID
            self.preview.updateFrame()

        def clearScroll(self):
            for widget in self.winfo_children():
                widget.destroy()

        def updateScroll(self):
            self.clearScroll()
            self.populateScroll()

    class PreviewFrame(ctk.CTkFrame):
        def __init__(self, master):
            super().__init__(master=master)
            self.modSesh = master.sesh

            self.songID = None
            self.grid(row=0, column=1, padx=(10, 10), pady=(10, 10), sticky="nsew")

            self.grid_rowconfigure((0, 1, 2), weight=1)
            self.grid_columnconfigure(0, weight=1)

            self.populateFrame()

        def populateFrame(self, clear=False):
            if clear or not self.songID:
                for i in range(3):
                    self.createItem(i, "")
                return
            
            songTimes = general.readJSON(songFile)
            songEntry = songTimes[self.songID]

            start, end = songEntry[0]
            artists = songEntry[1]
            song = songEntry[2]

            self.createItem(0, f"{self.modSesh.convertToStandard(start)}-{self.modSesh.convertToStandard(end)}")
            self.createItem(1, ", ".join(artists))
            self.createItem(2, song)

        def createItem(self, index, value):
            itemFrame = ctk.CTkFrame(
                self,
                fg_color=self.cget("fg_color")
            )
            itemFrame.grid_columnconfigure(0, weight=0)
            itemFrame.grid_columnconfigure(1, weight=1)

            if index == 0:
                text="Song Name: "
            elif index == 1:
                text="Artist Name: "
            else:
                text="Time Interval: "

            ctk.CTkLabel(
                itemFrame,
                text=text,
                font=headerfont,
                fg_color=itemFrame.cget("fg_color"),
            ).grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="w")

            ctk.CTkLabel(
                itemFrame,
                text=value,
                font=font,
                fg_color=itemFrame.cget("fg_color")
            ).grid(row=0, column=1, padx=(5, 5), pady=(5, 5), sticky="w")

            itemFrame.grid(row=index, column=0, padx=(25, 25), pady=(25, 25), sticky="nsew")

        def clearFrame(self):
            for widget in self.winfo_children():
                widget.destroy()

        def updateFrame(self):
            self.clearFrame()
            self.populateFrame()

    class ButtonFrame(ctk.CTkFrame):
        def __init__(self, master):
            super().__init__(master=master)
            self.sesh = master.sesh

            self.grid_columnconfigure((0, 1, 2), weight=1)
            self.grid_rowconfigure(0, weight=0)

            self.grid(row=1, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.populateFrame()

        def createButton(self, column, text, command, color):
            ctk.CTkButton(
                self,
                text=text,
                fg_color=color,
                text_color="white",
                width=75,
                height=50,
                command=command
            ).grid(row=0, column=column, padx=(10, 10), pady=(5, 5))

        def addPopup(self):
            songPopup = self.master.Popup(["Song Name", "Artist Name(s)"], "Verify Song")
            song, artist = songPopup.entryValues

            offSong, offArtist = self.sesh.searchSong(song, artist)

            general.notificationThread(
                "Song Found",
                f"{offSong} by {", ".join(offArtist)}"
            )

            timePopup = self.master.Popup(["Start Time (type start for starting of song)", "End Time (type end for ending of song)"], "Add Song Restriction")
            timeStart, timeEnd = timePopup.entryValues

            start, end = self.sesh.breakTime(timeStart), self.sesh.breakTime(timeEnd)
            if not self.sesh.checkTimes(start, end):
                general.notificationThread("Invalid Times Entered")
                return

            songID = self.sesh.getSongID(offSong, offArtist)

            self.sesh.logSongEntry([start, end], offArtist, offSong, songID)

            general.notificationThread(
                "Song Added Successfully"
            )

            self.refreshWindow()

        def removeSong(self):
            self.sesh.removeEntry(self.master.preview.songID)
            general.notificationThread(
                "Successfully removed"
            )
            self.refreshWindow()

        def modifyPopup(self):
            songID = self.master.preview.songID
            timePopup = self.master.Popup(["Start Time (type start for starting of song)", "End Time (type end for ending of song)"], "Add Song Restriction")
            timeStart, timeEnd = timePopup.entryValues

            start, end = self.sesh.breakTime(timeStart), self.sesh.breakTime(timeEnd)
            if not self.sesh.checkTimes(start, end):
                general.notificationThread("Invalid Times Entered")
                return

            self.sesh.modifyEntry(songID)

            general.notificationThread(
                "Song Interval Modified"
            )
            self.refreshWindow()

        def populateFrame(self):
            self.createButton(0, "Add Song", self.addPopup, "#098f01")
            self.createButton(1, "Remove Song", self.removeSong, "#f30207")
            self.createButton(2, "Modify Interval", self.modifyPopup, "#1371cc")

        def refreshWindow(self):
            self.master.scroll.updateScroll()
            self.master.preview.clearFrame()
            self.master.preview.populateFrame(clear=True)

    class Popup(ctk.CTkToplevel):
        def __init__(self, master, inputList: list, buttonName):
            super().__init__(master)
            self.nItems = len(inputList)
            self.inputList = inputList
            self.bName = buttonName

            self.geometry(f"200x{self.nItems*60}")
            self.grid_rowconfigure(list(range(self.nItems)), weight=1)
            self.grid_rowconfigure(self.nItems, weight=0)
            self.grid_columnconfigure(0, weight=1)

            self.populatePopup()

            self.mainloop()

        def createInputFrame(self, row):
            inputFrame = ctk.CTkFrame(
                self
            )
            inputFrame.grid(row=row, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            inputFrame.grid_rowconfigure((0, 1), weight=1)
            inputFrame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                inputFrame,
                text=f"Enter {self.inputList[row]}:"
            ).grid(row=0, column=0, padx=(5, 5), pady=(5, 5), sticky="nse")

            entry = ctk.CTkEntry(
                inputFrame
            )
            entry.grid(row=1, column=0, padx=(5, 5), pady=(5, 5), sticky="nsew")

        def populatePopup(self):
            for i in range(self.nItems):
                self.createInputFrame(i)

            ctk.CTkButton(
                self,
                text=self.bName,
                height=50,
                command=self.getEntries
            ).grid(row=self.nItems, column=0)

        def getEntries(self):
            self.entryValues = []
            for widget in self.winfo_children():
                if not isinstance(widget, ctk.CTkFrame):
                    continue
                for subwidget in widget.winfo_children():
                    if isinstance(subwidget, ctk.CTkEntry):
                        self.entryValues.append(subwidget.get())
            self.destroy()

    def __init__(self, fg_color = None):
        global font, color, headerfont
        color = fg_color
        super().__init__(fg_color)

        self.geometry("1400x600")

        self.title("Song Monitor")

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.grid_rowconfigure(1, weight=0)

        self.sesh = ModifySession()

        font = ctk.CTkFont(family="consolas", size=15)
        headerfont = ctk.CTkFont(family="consolas", size=20, weight="bold")

        self.createView()

    def createView(self):
        self.preview = self.PreviewFrame(self)
        self.scroll = self.ScrollFrame(self)
        self.buttons = self.ButtonFrame(self)

def run():
    songMonitor = SongMonitor()

    songMonitor.mainloop()

run()