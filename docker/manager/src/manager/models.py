from django.db import models


def dirty_image_path(instance, filename):
    return '%s/%s' % ("dirty_images", filename)


class DirtyImage(models.Model):
    image = models.ImageField(upload_to=dirty_image_path)
    is_published = models.BooleanField(default=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return "%s - %s" % (
            self.pk,
            self.image.path
        )
