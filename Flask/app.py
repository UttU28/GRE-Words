from flask import Flask, render_template, request, jsonify
import socket
import json

app = Flask(__name__)

@app.route('/')
def index():
    with open('greWords.json', 'r') as file:
        data = json.load(file)
    # data = {key: value for key, value in data.items() if value.get('clipsFound', 0) > 1}
    allData = list(data.keys())

    initialValue = 0
    maxValue = len(allData)
    return render_template('allWords.html', initialValue=initialValue, maxValue=maxValue, data=data, allData=allData)

    # for i in range(len(allData)):
    #     currentWord = allData[initialValue]
    #     currentData = data[currentWord]
    #     print(currentData)
    #     # currentMeaning = currentData["meaning"]
    #     # totalVideos = currentData["clipsFound"]
    # return render_template('allWords.html', initialValue=initialValue, currentWord=currentWord, currentData=currentData)

@app.route('/swipe', methods=['POST'])
def swipe():
    dataTemp = request.json
    print("Swiped card:", dataTemp)
    return jsonify({"message": "Swipe data received successfully!"})


if __name__ == '__main__':
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print(f"Host Name: {host_name}")
    print(f"Connect on Mobile: http://{ip_address}:5000")
    app.run(debug=True)