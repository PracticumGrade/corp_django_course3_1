from django.contrib import admin

from . import models


class PostAdmin(admin.ModelAdmin):
    # В этом классе опишем все настройки, какие захотим.
    ...


class CategoryAdmin(admin.ModelAdmin):
    # В этом классе опишем все настройки, какие захотим.
    ...


class LocationAdmin(admin.ModelAdmin):
    # В этом классе опишем все настройки, какие захотим.
    ...


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Location, LocationAdmin)
