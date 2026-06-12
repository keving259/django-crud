from django.urls import path
from .. import views

urlpatterns = [
    path('consultas_logs_menu/', views.consultas_logs_menu, name='consultas_logs_menu'),
    path('consultar_logs_clientes/', views.consultar_logs_clientes, name='consultar_logs_clientes'),
    path('consultar_logs_cuentas/', views.consultar_logs_cuentas, name='consultar_logs_cuentas'),
]
