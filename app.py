from components.core import process, process2
from components.utils import recipients
import json
from flask import Flask, request

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return 'Send a POST request here'
    jsonfile = request.json
    result = process(jsonfile)
    res = {"code": 200, "isUploaded": True, "allFlags": result}
    return res


@app.route('/api', methods=['GET', 'POST'])
def predict2():
    if request.method == 'GET':
        return 'Send An API Post Request Here'
    jsonfile = request.json
    # print(type(jsonfile))
    jsonfile = json.loads(jsonfile)
    # print(type(jsonfile))
    result = process2(jsonfile)
    res = {"code": 200, "isUploaded": True, "allFlags": result}
    return res


@app.route('/email', methods=['GET', 'POST'])
def email_sys():
    if request.method == 'GET':
        return 'Send An Email Request Here'
    jsonfile = request.json
    recipients(jsonfile)
    return "Email System Working"


if __name__ == '__main__':
    app.run()
