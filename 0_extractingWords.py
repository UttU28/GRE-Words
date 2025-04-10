import os
import json
import sys
from config import JSON_FILE, PDF_FILE, path_str

# Use PyMuPDF directly instead of fitz
try:
    import PyMuPDF as fitz
except ImportError:
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            print("Error: Could not import PyMuPDF.")
            print("Please install it with: pip install PyMuPDF==1.21.1")
            print("Or try: pip install --only-binary :all: PyMuPDF==1.21.1")
            sys.exit(1)

def readPDF(fileName):
    pdfDocument = fitz.open(fileName)
    textContent = ""
    for currentPage in range(pdfDocument.page_count):
        page = pdfDocument[currentPage]
        textContent += page.get_text()

    pdfDocument.close()
    return textContent

def getWordNumber(number):
    temp = str(number)
    return len(temp)+1, temp + "."

# Read PDF file using path from config
content = readPDF(path_str(PDF_FILE))

content = content.split("\n")
index = 1

newWordStructure = {"meaning": "", "wordIndex": 0, "wordUsed": False, "clipsFound": 0, "clipData": {}, "searched": False, "downloaded": False, "subtitleAdded": False}
greWords = {}
wordIndex = 1
currentIndex = 0
listLength = len(content)
currentWord, currentMeaning = "", ""
for i in range(len(content)):
    indexLength, indexString = getWordNumber(wordIndex)
    if content[i][:indexLength] == indexString:
        try:greWords[currentWord]["meaning"] = currentMeaning.strip()
        except:pass
        currentWord = content[i][indexLength:].strip()
        greWords[currentWord] = {"meaning": "", "wordIndex": wordIndex, "wordUsed": False, "clipsFound": 0, "clipData": {}, "searched": False, "downloaded": False, "subtitleAdded": False}
        wordIndex += 1
        currentMeaning = ""
    else:
        currentMeaning += content[i].strip() + " "

print(greWords)
print(greWords["abase"])

# Write to JSON file using path from config
with open(path_str(JSON_FILE), "w") as json_file:
    json.dump(greWords, json_file, indent=2)

print(f"Dictionary saved as JSON in '{path_str(JSON_FILE)}'.")
