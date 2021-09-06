
import os
from flask import Flask, request
app = Flask(__name__)


@app.route('/hello')
def hello():
    return 'Hello, world from node %s with ip: %s\n' \
        % (os.environ.get('NODE_NAME'), os.environ.get('NODE_IP'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)