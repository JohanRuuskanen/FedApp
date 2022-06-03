import numpy as np
import cv2
import pkg_resources
import io
import json
import socket
import requests
from flask import Flask, request, redirect, send_file
from flask_cors import CORS

BACKEND_URL = "http://backend.facedetect:5001"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
CORS(app)

def getForwardHeaders(request):
    headers = {}
    incomming_headers = [   
        'x-request-id',
        'x-b3-traceid',
        'x-b3-spanid',
        'x-b3-parentspanid',
        'x-b3-sampled',
        'x-b3-flags',
        'x-ot-span-context'
        ]

    for ihdr in incomming_headers:
        val = request.headers.get(ihdr)
        if val is not None:
            headers[ihdr] = val

    return headers

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):

            stream = file.read()
            r = requests.post(BACKEND_URL, files={'file': stream}, headers=getForwardHeaders(request))
            data = json.loads(r.text)

            img = np.asarray(bytearray(stream), dtype="uint8")
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            for (x,y,w,h) in data['faces']:
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
            frontendaddr = socket.gethostbyname(socket.gethostname())
            font = cv2.FONT_HERSHEY_SIMPLEX

            cv2.putText(img,"Frontend: "+frontendaddr,(20,20), font, .5,(255,55,55),1,cv2.LINE_AA)
            cv2.putText(img,"Backend: "+data['backendaddr'],(20,40), font, .5,(255,55,55),1,cv2.LINE_AA)

            img_encode = cv2.imencode('.jpg', img)[1]
            return send_file(
                io.BytesIO(img_encode),
                mimetype='image/jpeg',
                as_attachment=True,
                attachment_filename='faced.jpg')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File, new gunicorn settings!</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form> '''

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(port=5000,host='0.0.0.0')
