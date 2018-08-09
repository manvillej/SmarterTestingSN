from django.urls import path
from . import views
from django.contrib.auth import views as authviews

urlpatterns = [
    path('', views.UploadFormView.as_view(), name="index"),
    path('register', views.UserFormView.as_view(), name="register"),
    path('accounts/login/', authviews.LoginView.as_view(template_name='smartertesting/login.html'), name="login"),
    path('logout/', authviews.LogoutView.as_view(next_page= 'login'), name="logout"),
    path('uploads', views.uploads, name="uploads"),
    path('sn_objects', views.sn_objects, name="home"),
    path('sn_objects', views.sn_objects, name="sn_objects"),
    path('sn_tests', views.sn_tests, name="sn_tests"),
    path('upload_details/<int:upload_id>/', views.upload_details, name="upload_details"),
    path('sn_object_details/<int:object_id>/', views.sn_object_details, name="sn_object_details"),
    path('sn_test_details/<int:test_id>/', views.sn_test_details, name="sn_test_details"),
    path('test_relation', views.ObjectTestRelationFormView.as_view(), name="test_relation"),
]


