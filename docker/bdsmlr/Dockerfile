#syntax=docker/dockerfile:1
FROM python:3.10

WORKDIR /src

COPY src .

COPY ./docker/bdsmlr/requirements.txt .

COPY docker/bdsmlr/.env .

RUN if [ ! -d images ]; then mkdir images; fi

RUN python3 -m pip install -r requirements.txt
