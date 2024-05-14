from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='multiple_receipt'),
    path('upload_multiple/', views.upload_multiple_receipts, name='upload_multiple_receipts'),
    path('download_multiple/', views.download_multiple_receipt, name='download_multiple_receipt'),
    path('download_multiple/<str:filename>/', views.download_multiple_file, name='download_multiple_file')
    ]

