import PyPDF2
import re
import json
import random

def extractPdfContent(pdfPath):
    text = ""
    try:
        with open(pdfPath, 'rb') as pdfFile:
            reader = PyPDF2.PdfReader(pdfFile)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
    return text

def parseTextToWordMeaning(text):
    wordEntries = {}
    lines = text.split("\n")
    currentWord = None
    currentDefinition = []
    allWords = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r"^(\d+)\.", line)
        if match:
            if currentWord and currentDefinition:
                allWords.append((currentWord, " ".join(currentDefinition).strip()))
            currentWord = None
            currentDefinition = []
        elif currentWord is None:
            currentWord = line
        else:
            currentDefinition.append(line)

    if currentWord and currentDefinition:
        allWords.append((currentWord, " ".join(currentDefinition).strip()))

    totalWords = len(allWords)
    randomIndices = [f"{i:04d}" for i in range(totalWords)]  # Generate 4-digit indices
    random.shuffle(randomIndices)  # Shuffle the indices

    for index, (word, meaning) in enumerate(allWords):
        wordEntries[randomIndices[index]] = {
            "word": word,
            "meaning": meaning,
            "wordUsed": False,
            "clipsFound": 0,
            "clipData": {},
            "searched": False
        }

    return wordEntries

def saveToJson(data, outputPath):
    try:
        # Sort data by the key (4-digit number string)
        sortedData = {k: data[k] for k in sorted(data.keys())}
        
        with open(outputPath, 'w') as jsonFile:
            json.dump(sortedData, jsonFile, indent=4)
        print(f"Data successfully saved to {outputPath}")
    except Exception as e:
        print(f"An error occurred while saving to JSON: {e}")

def main():
    pdfPath = 'wordList.pdf'
    outputJsonPath = 'wordList.json'

    print("Extracting text from all pages of the PDF...")
    extractedText = extractPdfContent(pdfPath)

    print("Parsing text into words and meanings...")
    parsedData = parseTextToWordMeaning(extractedText)

    print("Saving parsed data to a JSON file...")
    saveToJson(parsedData, outputJsonPath)

if __name__ == "__main__":
    main()
