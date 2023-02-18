FROM python:3.10

WORKDIR /src

COPY ./docker/manager/src .

COPY ./docker/manager/requirements.txt .

RUN python3 -m pip install requirements.txt

