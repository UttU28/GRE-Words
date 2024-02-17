import fitz
import json
import random


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

fileName = "ManhattanPrep1000.pdf"
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


# SHUFFELIG THE DATA
shuffled_words = list(greWords.keys())
random.shuffle(shuffled_words)
shuffled_gre_words = {word: greWords[word] for word in shuffled_words}


fileName = "greWords.json"
with open(fileName, "w") as json_file:
    json.dump(shuffled_gre_words, json_file, indent=2)
    # json.dump(greWords, json_file, indent=2)

print(f"Dictionary saved as JSON in '{fileName}'.")
