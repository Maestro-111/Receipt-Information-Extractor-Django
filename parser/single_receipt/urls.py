# urls.py inside single_receipt app
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),  # http://127.0.0.1:8000/,
    path('upload/', views.upload_receipt, name='upload_receipt'),  # Updated URL pattern
    path('download/', views.download_receipt, name='download_receipt'),
    path('download/<str:filename>/', views.download_file, name='download_file')
]