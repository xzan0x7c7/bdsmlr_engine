#syntax=docker/dockerfile:1
FROM python:3.10

WORKDIR /src

COPY src .

COPY requirements.txt .

COPY docker/bdsmlr/entrypoint.sh entrypoint.sh

COPY docker/bdsmlr/.env .

RUN chmod +x entrypoint.sh

RUN if [ ! -d images ]; then mkdir images; fi

RUN python3 -m pip install -r requirements.txt

ENTRYPOINT ["/src/entrypoint.sh"]

CMD ["/bin/echo", "-h"]
