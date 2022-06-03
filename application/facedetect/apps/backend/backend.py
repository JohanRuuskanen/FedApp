import numpy as np
import cv2
import pkg_resources
import socket
from flask import Flask, request, redirect
from flask_cors import CORS

haar_xml = pkg_resources.resource_filename(
    'cv2', 'data/haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(haar_xml)

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        img = np.asarray(bytearray(request.files['file'].read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        backendaddr = socket.gethostbyname(socket.gethostname())

        return {"faces":[x.tolist() for x in faces],
                "backendaddr":backendaddr}

    return '''
    <!doctype html>
    <title>Backend</title>
    <h1>Backend, send POST with file</h1>
    </form> '''

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(port=5001,host='0.0.0.0')
