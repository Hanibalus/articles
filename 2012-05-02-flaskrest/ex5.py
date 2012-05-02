from flask import Flask, url_for
from flask import request
from flask import json
app = Flask(__name__)

from flask import Response

@app.route('/hello', methods = ['GET'])
def api_hello():
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    resp.headers['Link'] = 'http://luisrei.com'
    return resp
    

if __name__ == '__main__':
    app.run()
