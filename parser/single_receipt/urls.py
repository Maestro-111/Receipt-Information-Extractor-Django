# urls.py inside single_receipt app
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='single_receipt'),
    path('upload_single/', views.upload_receipt, name='upload_receipt'),
    path('download_single/', views.download_single_receipt, name='download_single_receipt'),
    path('download_single/<str:filename>/', views.download_file_single, name='download_file_single')
]