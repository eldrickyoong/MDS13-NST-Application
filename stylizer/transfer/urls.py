from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("gallery-images/", views.gallery_images, name="gallery-images"),
    path("gallery/", views.gallery, name="gallery"),
    path("style-images/", views.style_images, name="style_images"),
    path("stylize/", views.stylize, name="stylize"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
