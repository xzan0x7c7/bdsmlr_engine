## BDSMLR ENGINE

Download bdsmlr blog images.

### Run with Docker

Add environment variables on `docker/bdsmlr/.env` check the `.env.example` in that same directory, if any doubts.

- USERNAME - your bdsml username
- PASSWORD - your bdsmlr password


To run the compose feed since it's the only workable at the moment.

```
~$ docker-compose up --build --detach feed
```

Examples

```bash
~$ curl http://172.19.0.2:8888/get-env
~$ curl http://172.19.0.2:8888/get-blogs
~$ curl http://172.19.0.2:8888/get-ping
```
