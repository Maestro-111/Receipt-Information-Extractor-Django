# urls.py inside single_receipt app
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.main_menu),
    path('parse_single/', views.parse_single,name='parse_single'),
    path('parse_multiple/', views.parse_multiple,name='parse_multiple')
]