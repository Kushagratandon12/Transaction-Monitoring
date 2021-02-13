from processing import process, process2, recipients
import json
from functools import wraps
from flask import Flask, request, make_response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def predict():
    if request.method == 'GET':
        return 'Send a POST request here'
    jsonfile = request.json
    # print(type(jsonfile))
    # print(jsonfile)
    result = process(jsonfile)
    res = {"code": 200, "isUploaded": True, "allFlags": result}
    return res


@app.route('/api', methods=['GET', 'POST'])
def predict2():
    if request.method == 'GET':
        return 'Send An API Post Request Here'
    jsonfile = request.json
    print(type(jsonfile))
    jsonfile = json.loads(jsonfile)
    print(type(jsonfile))
    result = process2(jsonfile)
    res = {"code": 200, "isUploaded": True, "allFlags": result}
    return res


@app.route('/email', methods=['GET', 'POST'])
def email_sys():
    if request.method == 'GET':
        return 'Send An Email Request Here'
    jsonfile = request.json
    #jsonfile = json.loads(jsonfile)
    # print(type(jsonfile))
    # print(jsonfile)
    # print(type(jsonfile))
    recipients(jsonfile)
    return "Hi Kushagra Tandon/Bajpai Hero's"


if __name__ == '__main__':
    app.run()
