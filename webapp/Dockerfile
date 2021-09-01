FROM python:3.7

WORKDIR /opt/webapp

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
COPY templates/* ./templates/



ENTRYPOINT [ "python", "app.py" ]