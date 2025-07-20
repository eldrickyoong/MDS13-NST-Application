from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("about/", views.about, name="about"),
    path("style-images/", views.style_images, name="style_images"),
    path("stylize/", views.stylize, name="stylize"),
]
