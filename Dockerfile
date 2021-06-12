# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /vegebot

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY vegebot.py vegebot.py

COPY commands.py commands.py

COPY ticks ticks

CMD ["python3", "vegebot.py"]
