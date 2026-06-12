from django.urls import path
from .. import views

urlpatterns = [
    # Raíces y errores
    path('home/', views.home, name = 'home'),
    path('acceso_denegado/', views.acceso_denegado, name='acceso_denegado'),
    
    # Menus
    path('insertar/', views.insertar_menu, name='insertar_menu'),
    path('consultas/', views.consultas_menu, name='consultas_menu'),
    path('modificar_menu/', views.modificar_menu, name='modificar_menu'),
    
    # API
    path('api/estado_replicacion/', views.estado_replicacion, name='estado_replicacion')
]