import logging
import re

import requests
from django.conf import settings
from django.http import QueryDict
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from manager.models import DirtyImage


logger = logging.getLogger(__name__)


class ControlPanel(View):
    template_name = "manager/control-panel.html"
    def get(self, request):
        images = DirtyImage.objects.all()
        data = {"images" : images}
        return render(request, self.template_name, data)


class UploadDirtyImage(APIView):
    def post(self, request, *args, **kwargs):
        dirty_image = request.FILES.get("file")
        if dirty_image is None:
            return Response(
                data={
                    "message" : {
                        "error" : "Mising file"
                    },
                }, 
                status=400
            )
        dirty_image = DirtyImage.objects.create(
            image=dirty_image
        )
        return Response(
            data={
                "message" : {
                    "status" : "Dirty image saved."
                }
            }, 
            status=200
        )


class EnvStats(APIView):
    def get(self, request, *args, **kwargs):
        try:
            resp = requests.get(
                "%s/%s" % (
                    settings.FEED_URL, 
                    "env-stats"
                )
            )
            if resp.status_code != 200:
                raise Exception("Unable to get stats from feed") from None
        except Exception as error:
            logger.info(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : str(error)
                    }
                }, status=400
            )
        return Response(
            data={
                "message" : {
                    "env_stats" : resp.json()
                }
            }, 
            status=200
        )


class EnvSwitch(APIView):
    def post(self, request, *args, **kwargs):
        status = request.data.get("status")
        if status is None:
            return Response(
                data={
                    "message" : {
                        "error" : "Missing status on request body"
                    }
                }, 
                status=400
            )
        try:
            resp = requests.post(
                "%s/%s" % (
                    settings.FEED_URL, 
                    "on-off"
                ), 
                data={
                    "status" : status
                }
            )
            if resp.status_code != 200:
                raise Exception("Unable to set status %s" % status) from None
        except Exception as error:
            logger.info(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : str(error)
                    }
                }, 
                status=400
            )
        return Response(
            data={
                "message" : {
                    "status" : "Feed is %s" % status
                }
            }, 
            status=200
        )


class TriggerUpload(APIView):
    def post(self, request, *args, **kwargs):
        try:
            resp = requests.post(
                "%s/%s" % (
                    settings.FEED_URL,
                    "upload-images"
                )
            )
            if resp.status_code != 200:
                raise Exception("Unable to fetch images") from None
        except Exception as error:
            logger.info(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : str(error)
                    }
                }, 
                status=400
            )
        return Response(
            data={
                "message" : {
                    "status" : "New images fetched" 
                }
            }, 
            status=200
        )


class BlogsEndpoint(APIView):
    def get(self, request, *args, **kwargs):
        try:
            resp = requests.get(
                "%s/%s" % (
                    settings.FEED_URL, 
                    "get-blogs"
                )
            )
        except Exception as error:
            logger.exception(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : str(error)
                    }
                }, 
                status=400
            )
        return Response(
            data={
                "message" : {
                    "status" : resp.json()
                }
            }, 
            status=200
        )

    def post(self, request, *args, **kwargs):
        if request.data.get("blog") is None:
            data = {
                "message" : {
                    "error" : "Missing blog in the request body"
                }
            }
            return Response(
                data=data, 
                status=400
            )
        if not request.data.get("blog").endswith("bdsmlr.com"):
            data = {
                "message" : {
                    "error" : "Only bdsmlr.com blogs allowed."
                }
            }
            return Response(
                data=data, 
                status=400
            )
        try:
            check = requests.get(request.data.get("blog"))
            if check.status_code != 200:
                raise Exception(
                    "%s does not exist, pinged and obtained %s" % (
                        request.data.get("blog"),
                        check.status_code
                    )
                )
            check = re.search(
                r'This blog doesn\'t exist\.',
                check.content.decode("utf-8")
            )
            if check is not None:
                raise Exception(
                    "%s does not exist, pinged and obtained %s" % (
                        request.data.get("blog"),
                        "This blog doesn't exist"
                    )
                )
            resp = requests.post(
                "%s/%s" % (
                    settings.FEED_URL,
                    "add-blog"
                ),
                data={
                    "blog" : request.data.get("blog")
                }
            )
        except Exception as error:
            logger.exception(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : "Unable to add %s: Reason: %s" % (
                            request.data.get("blog"),
                            str(error)
                        )
                    }
                }, 
                status=400
            )
        return Response(
            data={
                "message" : {
                    "data" : resp.json()
                }
            }, 
            status=200
        )

    def delete(self, request):
        blog_id = request.GET.get("blog_id")
        if blog_id is None:
            return Response(
                data={
                    "message" : {
                        "error" : "Missing blog_id in request body"
                    }
                }, 
                status=400
            )
        try:
            resp = requests.post(
                "%s/%s" % (
                    settings.FEED_URL, 
                    "delete-blog"
                ),
                data={
                    "blog" : blog_id
                }
            )
            if resp.status_code != 200:
                raise Exception(
                    "Unable to delete %s" % blog_id
                ) from None
        except Exception as error:
            logger.error(str(error))
            return Response(
                data={
                    "message" : {
                        "error" : str(error)
                    }
                },
                status=400
            )
        return Response(
            data={
                "message" : {
                    "data" : resp.json()
                }
            },
            status=200
        )
