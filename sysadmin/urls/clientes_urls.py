from django.urls import path
from .. import views

urlpatterns = [
    path('agregar_cliente/', views.agregar_cliente, name="agregar_cliente"),
    path('consultas_clientes/', views.consultas_clientes, name='consultas_clientes'),
    path('clientes/modificar/<int:id>/', views.modificar_cliente, name='modificar_cliente'),
    path('clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('modificar_cliente/', views.modificar_cliente, name="modificar_cliente"),
    path('modificar_cliente/<int:id_cliente>/', views.modificar_cliente, name='modificar_cliente'),
]