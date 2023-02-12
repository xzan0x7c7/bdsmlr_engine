## BDSMLR ENGINE

Download bdsmlr blog images.

#### Extra Credits

The log in and link collection are take from this repository. and this script
specifically https://github.com/6fe9d454/bdsmlr-scripts/blob/master/bdsmlr_get_blog_fast.py

Some changes like true end page were making the script crash, or rendered it non
usable, also added download image functionality, refactored it, and dockerized it.

### Run with Docker

Add environment variables on `docker/bdsmlr/.env` check the `.env.example` in that same directory, if any doubts.

- USERNAME - your bdsml username
- PASSWORD - your bdsmlr password


#### Build Image

```
docker build --tag=bdsmlr:latest .
```

#### Run Container

Use the helper script, mounts bind; retreives images and make them
available. Run the command with `--help` option to see full options. 

```
~$./run_docker --help
```

