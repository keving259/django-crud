from django.conf import settings
from django.db import connection
import logging
from django.utils.timezone import now

def estado_replicacion(request):
    replicacion_activa = True 
    seconds_behind = 0  
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW SLAVE STATUS") 
            resultado = cursor.fetchone()
            if resultado:
                
                columnas = [col[0] for col in cursor.description]
                datos = dict(zip(columnas, resultado))
                
                io = datos.get("Slave_IO_Running")
                sql = datos.get("Slave_SQL_Running")
                replicacion_activa = io == 'Yes' and sql == 'Yes'
                lag = datos.get("Seconds_Behind_Master")
                seconds_behind = lag if isinstance(lag, int) else 0
    except Exception as e:
        logging.error(f"[Replicación] Error: {e}")
        replicacion_activa = False
        seconds_behind = 0

    return {
        'replicacion_activa': replicacion_activa,
        'seconds_behind': seconds_behind,
    }


# Context processor para incluir el tipo de usuario en todas las plantillas (se usó para pruebas)
def rol_usuario(request):
    tipo = request.session.get('tipo', None)
    return {'tipo': tipo}




def replicacion_context(request):
    try:
        # Context processor para incluir el estado de la replicación y el lag en todas las plantillas
        from .views import ver_lag_replicacion
        replicacion_activa, _ = ver_lag_replicacion()
    except:
        replicacion_activa = False

    return {
        'replicacion_activa': replicacion_activa
    }

    
def estado_usuario(request):
    if request.session.get('usuario'):
        return {'estado_usuario': 'Conectado'}
    else:
        return {'estado_usuario': 'Desconectado'}

def hora_utc_actual(request):
    return {'hora_utc_actual': now()}