import datetime
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
        self.on = False
        self.streak_limit = "5"
        self.max_images = "15"
        self.blogs = {}
        self.start_time = datetime.datetime.timestamp(
            datetime.datetime.now()
        )
        self.runs = {
            "main_runs" : 0, 
            "blog_runs" : []
        }
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
        if not Env.on:
            logger.info("Engine is off ..")
            return True
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
        message="pong"
    ), 200


@app.route("/on-off", methods=["POST"])
def switch_env():
    status = request.form.get("status")
    if status is None:
        return jsonify(
            message="Missing status"
        ), 400
    if status.lower() not in ["on", "off"]:
        return jsonify(
            message="status not one of on|off"
        ), 400
    op = Env.on_switch(status)
    if op:
        return jsonify(
            message="Status: %s" % status
        ), 200
    return jsonify(
        message="Unable to change status"
    ), 400


@app.route("/env-stats", methods=["GET"])
def env_stats():
    data = {
        "env" : {
            "on" : "no" if not Env.on else "yes",
            "runs" : Env.runs,
            "loaded_blogs" : Env.blogs,
            "start_time" : Env.start_time,
            "settings" : {
                "max_images" : Env.max_images,
                "streak_limit" : Env.streak_limit
            }
        }
    }
    return jsonify(
        data=data
    ), 200


@app.route("/get-blogs", methods=["GET"])
def get_blogs():
    return jsonify(
        blogs=Env.blogs
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
    

@app.route("/delete-blog", methods=["POST"])
def delete_blog():
    blog = request.form.get("blog")
    if blog is None:
        return jsonify(
            status=False,
            message="missing blog"
        )
    try:
        int(blog)
    except Exception as error:
        logger.error(str(error))
        return jsonify(
            message="Blog keys only"
        ), 400
    try:
        to_delete = Env.blogs[int(blog)]
    except KeyError:
        return jsonify(
            message="%s does not exist" % blog
        ), 400
    if not Env.delete_blog(
            int(
                blog
            )
        ):
        return jsonify(
            status=False, 
            message="Unable to delete %s" % to_delete
        ), 400
    return jsonify(
        status=True,
        message="Blog %s deleted" % to_delete
    ), 200


@app.route("/set-attr", methods=["POST"])
def set_attr():
    attr = request.form.get("attr")
    value = request.form.get("value")
    if attr is None or value is None:
        return jsonify(
            message="Missing form data, need attr and value"
        ), 400
    if not hasattr(Env, attr):
        return jsonify(
            message="Invalid %s attr" % attr
        ), 400
    if attr not in ["max_images", "streak_limit"]:
        return jsonify(
            message="Can only set max_images, streak_limit"
        ), 400
    try:
        int(value)
    except Exception as error:
        return jsonify(
            message="Only integers for values"
        )
    setattr(
        Env, 
        attr, 
        value
    )
    return jsonify(
        message="%s set to %s" % (attr, value)
    ), 200


if __name__ == "__main__":
    logger.info(
        "BDSML FEED started, current status: ON: %s " % Env.on
    )
    app.run(
        debug=True, 
        host="0.0.0.0", 
        port=8888
    )
