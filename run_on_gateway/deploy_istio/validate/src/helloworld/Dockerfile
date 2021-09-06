FROM python:2-onbuild

WORKDIR /opt/app
COPY app.py /opt/app/

EXPOSE 5000

WORKDIR /opt/app
CMD ["python", "app.py"]