from django.contrib import admin

from manager.models import DirtyImage

@admin.register(DirtyImage)
class AdminDirtyImage(admin.ModelAdmin):
    list_display = ['pk', 'created_at', 'image']

