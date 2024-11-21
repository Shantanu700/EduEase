from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("register/", views.register),
    path("signin/", views.signin),
    path("logout/", views.signout, name="logout"),
    path("upload_doc/", views.upload_document),
    path("ask_question/", views.ask_question),
    path("flash_card/", views.get_fl_card),

]