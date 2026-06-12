from django.urls import path, include

urlpatterns = [
    # Rutas generales
    path('', include('sysadmin.urls.base_urls')),
    
    # Rutas de autenticación y sesión
    path('', include('sysadmin.urls.auth_urls')),
    
    # Rutas para clientes
    path('clientes/', include('sysadmin.urls.clientes_urls')),
    
    # Rutas para cuentas
    path('cuentas/', include('sysadmin.urls.cuentas_urls')),
    
    # Rutas para logs
    path('logs/', include('sysadmin.urls.logs_urls')),
]
