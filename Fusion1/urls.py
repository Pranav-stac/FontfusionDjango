from django.urls import path
from . import views
from django.urls import path, include
from django.urls import path
from Fusion1.views import UserCreate, LoginView

from rest_framework.routers import DefaultRouter
# from .views import FontModelViewSet,get_csrf_token

router = DefaultRouter()
# router.register(r'fonts', FontModelViewSet)

urlpatterns = [
    #    path('', views.index, name='index'),
      #  path('process-images/', views.image_process_view, name='process-images'),
       path('image_process_api/', views.image_process_api, name='image_process_api'),
       path('get-font/', views.send_font_file, name='get-font'),
       path('funky-font/', views.send_random_font_file, name='funky-font'),
       path('api/register/', UserCreate.as_view(), name='register'),
       path('api/login/', LoginView.as_view(), name='login'),
       path('latext/', views.convert_to_latex, name='latext'),
       path('decode_image/', views.decode_image, name='decode_image'),
       path('handwritten/', views.handwritten, name= 'handwritten'),
    #    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
   ]

