FROM python:3.7

WORKDIR /opt/client

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY run.py .

ENTRYPOINT [ "python", "run.py" ]