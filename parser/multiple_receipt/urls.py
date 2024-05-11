from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='multiple_receipt'),
    path('upload_multiple/', views.upload_multiple_receipts, name='upload_multiple_receipts'),
    ]

