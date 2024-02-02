from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
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