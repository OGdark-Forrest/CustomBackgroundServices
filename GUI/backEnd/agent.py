from . import model
from utils.imports import *

class SummaryAgent:
    def call(self, conversation: str) -> tuple[str, str]:
        context = self.get_context(conversation)
        return context

    def save(self, conversation: str) -> str:
        return self.create_summary_file(conversation)

    def load_context(self, lfiles: list) -> str:
        context = ""
        if not lfiles:
            context = "No previous context"
        else:
            for file in lfiles:
                with open("GUI/backEnd/runtimeFiles/summaryFiles/"+file, encoding="utf-8") as rfile:
                    context += rfile.read()
        
        return context

    def get_context(self, conversation: str) -> str:
        with open("GUI/backEnd/runtimeFiles/csvFiles/summaryFiles.csv", newline="", encoding="utf-8") as rfile:
            filenames = ""
            reader = csv.reader(rfile)
            for line in reader:
                filenames += line[0] + " " + line[1]
        
        del reader
        prompt = f"""
        {conversation}
        For the list of below filenames select ONLY THOSE which are MOST RELEVANT to the above conversation:
        Give the names of the files NEWER to OLDER from LEFT to RIGHT
        {filenames}

        If no such file return NONE.

        Format: <filenames>(comma separated)(no spaces or newlines)
        
    """

        fileList = model.get_content(prompt)
        if fileList == "NONE":
            context = self.load_context([])
        else:
            context = self.load_context(fileList.split(","))

        return context

    def load_summary(self, lfiles: list) -> str:
        summary = ""
        if not lfiles:
            summary = "No previous summary"
        else:
            for file in lfiles:
                with open("GUI/backEnd/runtimeFiles/summaryFiles/"+file, encoding="utf-8") as rfile:
                    summary += rfile.read()
        
        return summary
    
    def generate_summary(self, conversation: str) -> tuple[str, str]:
        with open("GUI/backEnd/runtimeFiles/csvFiles/summaryFiles.csv", newline="", encoding="utf-8") as rfile:
            l = []
            reader = csv.reader(rfile)
            for line in reader:
                l.append(line[1])
        summary = self.load_summary(l)

        prompt = f"""\n
        For the below conversation, generate a summary. DO NOT MISS ANY POTENTIALLY USEFUL OR RELEVANT INFORMATION.
        Also suggest a SHORT and appropriate file name to store this summary which contains relevant keywords.

        If no useful information AT ALL, return NONE
        
        Format of Response:
        FileName:<filename>
        Summary:
        <Summary>
        
        {conversation}\n"""

        content = model.get_content(prompt)

        if content == "NONE":
            return False, False

        fileName = content[9:content.find("\n")]
        summary = content[content.find("Summary:")+9:]

        return fileName, summary

    def create_summary_file(self, conversation: str) -> str:
        fname, summary = self.generate_summary(conversation)

        if not summary or not fname:
            return

        with open("GUI/backEnd/runtimeFiles/summaryFiles/"+fname, "w", encoding="utf-8") as wfile:
            wfile.write(summary+"\n")
        with open("GUI/backEnd/runtimeFiles/csvFiles/summaryFiles.csv", "a", newline="", encoding="utf-8") as afile:
            writer = csv.writer(afile)
            writer.writerow([time.strftime('%X %x'), fname])
        
        return f"Summary file {fname} successfully saved"
