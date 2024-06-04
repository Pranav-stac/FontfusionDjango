from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FontModelViewSet

router = DefaultRouter()
router.register(r'fonts', FontModelViewSet)

urlpatterns = [
       path('', views.index, name='index'),
       path('process-images/', views.image_process_view, name='process-images'),
       path('image_process_api/', views.image_process_api, name='image_process_api'),
   ]

