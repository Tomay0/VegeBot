# syntax=docker/dockerfile:1

FROM python:3.8-alpine

WORKDIR /vegebot

# install dependencies
# libffi-dev openssl-dev python3-dev
RUN apk add --no-cache ffmpeg build-base python3-dev libffi-dev
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# copy program
COPY vegebot.py vegebot.py
COPY commands.py commands.py
COPY config.yml config.yml

CMD ["python3", "vegebot.py"]