from django.urls import path

from manager.views import UploadDirtyImage

app_name = "manager"


urlpatterns = [
    path(
        "upload-dirty-image", 
        view=UploadDirtyImage.as_view(),
        name="upload_dirty_image"
    )
]
