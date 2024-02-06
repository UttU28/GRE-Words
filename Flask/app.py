from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
import json

app = Flask(__name__)
logFilePath = 'userAccessLogs.json'


def saveUserAccessData():
    accessCounter = {}
    try:
        with open(logFilePath, 'r') as file:
            accessCounter = json.load(file)
    except FileNotFoundError:
        with open(logFilePath, 'w') as file:
            json.dump(accessCounter, file)
    todayDate = date.today().strftime('%m/%d/%y')
    accessCounter[todayDate] = accessCounter.get(todayDate, 0) + 1
    with open(logFilePath, 'w') as file: json.dump(accessCounter, file, indent=2)

@app.route('/')
def index():
    saveUserAccessData()
    with open('greWords.json', 'r') as file:
        data = json.load(file)
    data = {key: value for key, value in data.items() if value.get('clipsFound', 0) > 1}
    allData = list(data.keys())

    initialValue = 0
    maxValue = len(allData)
    print(maxValue)
    return render_template('allWords.html', initialValue=initialValue, maxValue=maxValue, data=data, allData=allData)

@app.route('/swipe', methods=['POST'])
def swipe():
    dataTemp = request.json
    print("Swiped card:", dataTemp)
    return jsonify({"message": "Swipe data received successfully!"})


if __name__ == "__main__":
    # app.run()
    # app.run(host="0.0.0.0", port=443)
    app.run(host="0.0.0.0", port=5000)