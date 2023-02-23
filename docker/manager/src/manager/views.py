import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from manager.models import DirtyImage


class UploadDirtyImage(APIView):
    
    def post(self, request, *args, **kwargs):
        dirty_image = request.FILES.get("file")
        if dirty_image is None:
            return Response(
                data={
                    "message" : "Mising file",
                }, 
                status=400
            )
        dirty_image = DirtyImage.objects.create(
            image=dirty_image
        )
        return Response(
            data={
                "message" : "Dirty image saved."
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
                    "message" : str(error)
                }, status=400
            )
        data = {
            "message" : {
                "env-stats" : resp.json()
            }
        }
        return Response(data=data, status=200)


class EnvSwitch(APIView):

    def post(self, request, *args, **kwargs):
        status = request.data.get("status")
        if status is None:
            data = {
                "message" : "Missing status on request body"
            }
            return Response(data=data, status=400)
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
            data = {
                "message" : str(error)
            }
            return Response(data=data, status=400)
        data = {
            "message" : {
                "status" : "Feed is %s" % status
            }
        }
        return Response(data=data, status=200)


class TriggerUpload(APIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class AddBlog(APIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class DeleteBlog(APIView):
    def post(self, request, *args, **kwargs):
        raise NotImplementedError()


class GetBlogs(APIView):
    def get(self, request, *args, **kwargs):
        raise NotImplementedError()

