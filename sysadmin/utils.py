from django.db import connection
import logging
import ipaddress

logger = logging.getLogger(__name__)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    logger.debug(f"IP detectada: {ip} para la petición {request.path}")
    return ip

def validar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def obtener_lag_replicacion():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW SLAVE STATUS")
            result = cursor.fetchone()
            if result:
                columnas = [col[0] for col in cursor.description]
                data = dict(zip(columnas, result))
                lag = data.get('Seconds_Behind_Master')
                return int(lag) if lag is not None else 'Desconocido'
            else:
                return None
    except Exception as e:
        print("ERROR OBTENIENDO LAG:", e)
        return 'Desconocido'
