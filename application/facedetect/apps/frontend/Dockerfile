FROM python:3.6.8

LABEL reason=FacedetectFrontend

WORKDIR /app
COPY . /app

RUN pip install -r /app/requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000" , "frontend:app", \
        "--worker-tmp-dir", "/dev/shm", \
        "--log-file", "-", \
        "--log-level", "info", \ 
        "--workers" , "9", \
        "--worker-class", "gevent", \
        "--worker-connections", "1000"]
