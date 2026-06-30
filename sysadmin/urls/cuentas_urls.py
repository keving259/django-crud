from django.urls import path
from .. import views

urlpatterns = [
    path('agregar_cuenta/', views.agregar_cuenta, name="agregar_cuenta"),
    path('consultas_cuentas/', views.consultas_cuentas, name='consultas_cuentas'),
    path('cuentas/modificar/<int:id>/', views.modificar_cuenta, name='modificar_cuenta'),
    path('cuentas/eliminar/<int:id_cuenta>/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('modificar_cuenta/', views.modificar_cuenta, name='modificar_cuenta'),
    path('modificar_cuenta/<int:id_cuenta>/', views.modificar_cuenta, name='modificar_cuenta'),
]
