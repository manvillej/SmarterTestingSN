from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.UploadFormView.as_view(), name="index"),
    path('test_relation', views.ObjectTestRelationFormView.as_view(), name="test_relation"),
]

