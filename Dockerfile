# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /vegebot

# install dependencies
RUN apk add --no-cache ffmpeg build-base python3-dev libffi-dev postgresql-dev
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy program
COPY vegebot_src/* ./

CMD ["python3", "vegebot.py"]
