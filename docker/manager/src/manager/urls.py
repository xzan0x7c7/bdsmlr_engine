from django.urls import path

from manager import views

app_name = "manager"


urlpatterns = [
    path(
        "upload-dirty-image", 
        view=views.UploadDirtyImage.as_view(),
        name="upload_dirty_image"
    ),
    path(
        "feed-stats",
        view=views.EnvStats.as_view(),
        name="feed_stats"
    ),
    path(
        "feed-switch",
        view=views.EnvSwitch.as_view(),
        name="feed_switch"
    ),
    path(
        "trigger-upload",
        view=views.TriggerUpload.as_view(),
        name="trigger_upload"
    ),
    path(
        "blogs",
        view=views.BlogsEndpoint.as_view(),
        name="blogs"
    ),
]
