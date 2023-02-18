## BDSMLR ENGINE

Download bdsmlr blog images.

#### Next Steps (TO DO)

- [ ] Make a small flask/django app for serving and viewing images.
    - [ ] Trigger pulls by default.
    - [ ] Add option to repost, reblog downloaded images directly from panel.
    - [ ] Add asynchronous tasks
    - [ ] Monitor tasks.
- [ ] Create docker-compose file.

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

### Credit where credit is due.

The log in and link collection are take from this repository, this script
specifically https://github.com/6fe9d454/bdsmlr-scripts/blob/master/bdsmlr_get_blog_fast.py

Some things like `true_end_page` were making the script crash, or rendered it non
usable, added download image functionality, refactored it, and dockerized it.
