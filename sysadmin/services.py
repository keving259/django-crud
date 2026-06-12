import json
from django.db import connection, connections
from django.shortcuts import render, redirect
from django.db import connections
from django.conf import settings

def verificar_cliente_existe(id_cliente):
    with connection.cursor() as cursor:
        cursor.callproc('cliente_existe_proc', [id_cliente])
        return cursor.fetchone()[0] > 0

def autenticar_usuario_bd(correo, password, ip_cliente, zona_horaria):
    with connection.cursor() as cursor:
        cursor.execute('SET @resultado = NULL;')
        cursor.execute('CALL log_in(%s, %s, %s, %s, @resultado);', [correo, password, ip_cliente, zona_horaria])
        cursor.execute('SELECT @resultado')
        resultado = cursor.fetchone()[0]

    try:
        resultado_json = json.loads(resultado)
        return resultado_json
    except Exception as e:
        print("Error al parsear JSON: ", e)
        raise ValueError("Error de respuesta del servidor")

def registrar_cliente_bd(nombre, apellido, telefono, correo, direccion, created_by, zona, ip):
    with connection.cursor() as cursor:
        cursor.callproc('agregar_cliente', [
            nombre, apellido, telefono, correo,
            direccion, created_by, zona, ip
        ])

def registrar_cuenta_bd(id_cliente, estado, created_by, ip_cliente, zona_horaria):
    if not verificar_cliente_existe(id_cliente):
        raise ValueError("El cliente con ID {} no existe.".format(id_cliente))
    
    with connection.cursor() as cursor:
        cursor.callproc('agregar_cuenta', [
            id_cliente, estado, created_by, ip_cliente, zona_horaria
        ])

def obtener_sugerencias_clientes_bd():
    sugerencias = []
    try:
        with connection.cursor() as cursor:
            cursor.callproc('obtener_sugerencias_sin_cuenta')
            for id_cliente, nombre_completo in cursor.fetchall():
                sugerencias.append(f'{id_cliente} - {nombre_completo}')
    except Exception as e:
        print(f'[ERROR] No se pudieron cargar sugerencias de clientes: {e}')
    return sugerencias

def obtener_ids_clientes_bd():
    try:
        with connections['default'].cursor() as cursor:
            cursor.callproc('obtener_ids_clientes')
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f'[ERROR] No se pudieron cargar IDs de clientes: {e}')
        return []

def obtener_cliente_por_id_bd(id_cliente):
    try:
        with connections['default'].cursor() as cursor:
            cursor.callproc('obtener_cliente_por_id', [id_cliente])
            row = cursor.fetchone()
            if row:
                rows = [col[0] for col in cursor.description]
                return dict(zip(rows, row))
    except Exception as e:
        print(f'[ERROR] No se pudo obtener cliente por ID: {e}')
    return None

def modificar_cliente_bd(id_cliente, nombre, apellido, telefono, correo, direccion, modified_by, deleted, zona_horaria, ip_cliente):
    with connections['default'].cursor() as cursor:
        cursor.callproc('modificar_cliente', [
            id_cliente, nombre, apellido, telefono, correo,
            direccion, modified_by, deleted, zona_horaria, ip_cliente
        ])

def obtener_ids_cuentas_bd():
    try:
        with connections['replica'].cursor() as cursor:
            cursor.callproc('obtener_ids_cuentas')
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f'[ERROR] No se pudieron cargar IDs de cuentas: {e}')
        return []

def obtener_cuenta_por_id_bd(id_cuenta):
    try:
        with connections['replica'].cursor() as cursor:
            cursor.callproc('obtener_cuenta_por_id', [id_cuenta])
            row = cursor.fetchone()
            if row:
                rows = [col[0] for col in cursor.description]
                return dict(zip(rows, row))
    except Exception as e:
        print(f'[ERROR] No se pudo obtener cuenta por ID: {e}')
    return None

def modificar_cuenta_bd(id_cuenta, id_cliente, estado, modified_by, deleted, zona_horaria, ip_cliente):
    with connections['default'].cursor() as cursor:
        cursor.callproc('modificar_cuenta', [
            id_cuenta, id_cliente, estado, modified_by, deleted, zona_horaria, ip_cliente
        ])

def buscar_clientes_bd(nombre, telefono, correo, direccion, registro):
    try:
        with connections['replica'].cursor() as cursor:
            cursor.callproc('p_clientes', [
                nombre, telefono, correo, direccion, registro
            ])
            rows = [col[0] for col in cursor.description]
            return [dict(zip(rows, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f'[ERROR] No se pudieron buscar clientes: {e}')
        raise e

def buscar_cuentas_bd(id_cuenta, nombre, telefono, correo):
    try:
        with connections['replica'].cursor() as cursor:
            cursor.callproc('p_cuentas', [
                id_cuenta, nombre, telefono, correo
            ])
            rows = [col[0] for col in cursor.description]
            return [dict(zip(rows, row)) for row in cursor.fetchall()]
    except Exception as e:
        print(f'[ERROR] No se pudieron buscar cuentas: {e}')
        raise e

def eliminar_cliente_bd(id_cliente, modified_by, zona_horaria, ip_cliente):
    with connections['default'].cursor() as cursor:
        cursor.callproc('eliminar_cliente_proc', [
            id_cliente, modified_by, zona_horaria, ip_cliente
        ])

def eliminar_cuenta_bd(id_cuenta, modified_by, zona_horaria, ip_cliente):
    with connections['default'].cursor() as cursor:
        cursor.callproc('eliminar_cuenta_proc', [
            id_cuenta, modified_by, zona_horaria, ip_cliente
        ])

def buscar_logs_clientes_bd(fecha_inicio, fecha_fin, tipo_operacion):
    results = []
    try:
        with connections as cursor:
            cursor.callproc('buscar_logs_clientes', [fecha_inicio, fecha_fin, tipo_operacion])
            
            rows = [col[0] for col in cursor.description]
            raw_results = cursor.fetchall()
            
            for row in raw_results:
                row_dict = dict(zip(rows, row))
                
                row_list = list(row)
                for idx in [5, 6]:
                    if idx < len(row_list) and row_list[idx]:
                        try:
                            data = json.loads(row_list[idx])
                            row_list[idx] = sorted(data.items())
                        except Exception:
                            pass
                
                results.append(dict(zip(rows, row_list)))
            return results
    except Exception as e:
        print(f'[ERROR] No se pudieron buscar logs de clientes: {e}')
        raise e

def buscar_logs_cuentas_bd(fecha_inicio, fecha_fin, tipo_operacion):
    results = []
    try:
        with connections['replica'].cursor() as cursor:
            cursor.callproc('buscar_logs_cuentas', [fecha_inicio, fecha_fin, tipo_operacion])
            
            rows = [col[0] for col in cursor.description]
            raw_results = cursor.fetchall()
            
            for row in raw_results:
                row_dict = dict(zip(rows, row))
                
                row_list = list(row)
                for idx in [5, 6]:
                    if idx < len(row_list) and row_list[idx]:
                        try:
                            row_list[idx] = json.loads(row_list[idx])
                        except Exception:
                            row_list[idx] = None
                    elif idx < len(row_list):
                        row_list[idx] = None
                
                results.append(dict(zip(rows, row_list)))
            return results
    except Exception as e:
        print(f'[ERROR] No se pudieron buscar logs de cuentas: {e}')
        raise e

def registrar_usuario_db(nombre_usuario, nombre_completo, correo, telefono, password, rol, estado, created_by, zona, ip):
    with connections['default'].cursor() as cursor:
        cursor.execute("""
            CALL agregar_usuario(%s, %s, %s, %s, %s, %s, %s, %s, %s);
            )
        """, [nombre_usuario, nombre_completo, correo, telefono, password, rol, estado, created_by, zona, ip])

def obtener_estado_replicacion_bd():
    if settings.DEBUG:
        return {'replicacion_activa' : True, 'lag_replicacion': 0, 'modo_debug': True}
    try:
        with connections['replica'].cursor() as cursor:
            cursor.execute('SHOW SLAVE STATUS')
            resultado = cursor.fetchone()
            
            if not resultado:
                return {'replicacion_activa': False, 'lag_replicacion': None, 'modo_debug': False}
            
            rows = [col[0] for col in cursor.description]
            data = dict(zip(rows, resultado))
            
            io_running = data.get('Slave_IO_Running') == 'Yes'
            sql_running = data.get('Slave_SQL_Running') == 'Yes'
            replicacion_activa = io_running and sql_running
            
            lag = data.get('Seconds_Behind_Master')
            
            return {
                'replicacion_activa' : replicacion_activa,
                'seconds_behind_master': lag
            }
            
    except Exception as e:
        print(f'[ERROR] No se pudo obtener estado de replicación: {e}')
        return {'replicacion_activa': False, 'lag_replicacion': None}