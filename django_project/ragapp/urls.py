from django.urls import path
from . import views

app_name = 'ragapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('ask/', views.ask, name='ask'),
]
