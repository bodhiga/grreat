FROM python:3.9

WORKDIR /usr/src/app
COPY requirements.txt requirements-dev.txt .
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
