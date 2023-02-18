import json
import logging
import os
import subprocess
import sys

import requests
from flask import Flask, jsonify, request
from flask_apscheduler import APScheduler

from settings import THIS_DIR
from logger import get_logger


app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


logger = get_logger(__name__)


class Environment(object):
    def __init__(self):
        self.on = True
        self.runs = {
            "main_runs" : 0, 
            "blog_runs" : []
        }
        self.streak_limit = "5"
        self.max_images = "15"
        self.blogs = {}
        with open(os.path.join(THIS_DIR, "blog_urls.txt"), "r") as ts:
            data = ts.readlines()
            for d, i in enumerate(data, 0):
                self.blogs[d] = i.strip("\n")

    def on_switch(self, status):
        if status == "on":
            self.on = True
        else:
            self.on = False
        return True

    def get_runs(self):
        return self.runs
    
    def get_blogs(self):
        return self.blogs

    def get_blog_by_id(self, i):
        try:
            blog = self.blogs[i]
        except Exception as error:
            logger.error(str(error))
            return None
        return blog
    
    def add_blog(self, blog):
        try:
            last_key = sorted(self.blogs.keys())[-1]
            new_key = last_key + 1
            self.blogs[new_key] = blog
        except Exception as error:
            logger.error(str(error))
            return False
        return True

    def delete_blog(self, pk):
        try:
            self.blogs.pop(pk)
        except Exception as error:
            logger.info(str(error))
            return False
        return True

    def make_runs(self):
        if not self.on:
            return False
        for each in self.blogs:
            logger.info("getting blog: %s" % self.blogs[each])
            r1 = subprocess.run(
                [
                    sys.executable, 
                    "bdsmlr.py",
                    self.blogs[each],
                    "--streak-limit=%s" % self.streak_limit,
                    "--max-images=%s" % self.max_images,
                ],
                capture_output=True
            )
            if r1.returncode == 0:
                logger.info("success")
                self.runs["blog_runs"].append(
                    [
                        True, 
                        self.blogs[each]
                    ]
                )
            else:
                logger.info("error: %s" % r1.stderr.decode("utf-8"))
                self.runs["blog_runs"].append(
                    [
                        False, 
                        self.blogs[each]
                    ]
                )
            

Env = Environment()


@scheduler.task(
    'cron', 
    id='make_runs', 
    hour="*/1",
    minute="1"
)
def make_runs():
    try:
        Env.make_runs()
        Env.runs["main_runs"] += 1
    except Exception as error:
        logger.exception(str(error))
        return False
    logger.info("Finished main run %s" % Env.runs["main_runs"])
    return True


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify(
        status=True, 
        message="pong"
    ), 200


@app.route("/on-off", methods=["POST"])
def switch_env():
    status = request.form.get("status")
    if status is None:
        return jsonify(
            status=False,
            message="Missing status"
        ), 400
    if status.lower() not in ["on", "off"]:
        return jsonify(
            status=False, 
            message="status not one of on|off"
        ), 400
    op = Env.on_switch(status)
    if op:
        return jsonify(
            status=True,
            message="Status: %s" % status
        ), 200
    return jsonify(
        status=False,
        message="Unable to change status"
    ), 400


@app.route("/env-stats", methods=["GET"])
def env_stats():
    data = {
        "env" : Env.get_runs()
    }
    return jsonify(
        status=True, 
        data=data
    ), 200


@app.route("/get-blogs", methods=["GET"])
def get_blogs():
    return jsonify(
        blogs=Env.get_blogs()
    ), 200


@app.route("/add-blog", methods=["POST"])
def add_blog():
    blog = request.form.get("blog")
    if blog is None:
        return jsonify(
            status=False,
            message="missing blog"
        )
    if not Env.add_blog(blog):
        return jsonify(
            status=False, 
            message="Unable to add %s" % blog
        ), 400
    return jsonify(
        status=True,
        message="Blog %s added" % blog
    ), 200
    

if __name__ == "__main__":
    app.run(
        debug=True, 
        host="0.0.0.0", 
        port=8888
    )
