from django.urls import path
from .. import views

urlpatterns = [
    # Raíces
    path('home/', views.home, name = 'home'),
    
    # API
    path('api/estado_replicacion/', views.estado_replicacion, name='estado_replicacion')
]