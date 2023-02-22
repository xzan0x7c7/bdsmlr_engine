from rest_framework.views import APIView
from rest_framework.response import Response

from manager.models import DirtyImage


class UploadDirtyImage(APIView):
    
    def post(self, *args, **kwargs):
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
