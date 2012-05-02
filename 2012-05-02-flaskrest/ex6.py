from flask import Flask, url_for
from flask import request
from flask import json
app = Flask(__name__)

from flask import Response
from flask import jsonify

@app.route('/hello', methods = ['POST'])
def api_hello():
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    resp = jsonify(data)
    resp.headers['Link'] = 'http://luisrei.com'
    resp.status_code = 201
    return resp
    

if __name__ == '__main__':
    app.run()
