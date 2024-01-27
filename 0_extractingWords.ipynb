import fitz
import json

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

fileName = "wordList.pdf"
content = readPDF(fileName)

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

fileName = "greWords.json"
with open(fileName, "w") as json_file:
    json.dump(greWords, json_file, indent=2)

print(f"Dictionary saved as JSON in '{fileName}'.")
