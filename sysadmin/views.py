from django.shortcuts import render, redirect
from django.db import connection, connections
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from functools import wraps
from sysadmin.context_processors import estado_replicacion
from .models import Log
from .forms import MiFormulario, LoginForm, ClientForm, CuentaForm, ModiciarClienteForm, ModificarCuentaForm, FiltroClienteForm, FiltroCuentasForm, FiltroLogsForm, SignupStep1Form, SignupStep2Form
from django.utils.timezone import now
from .utils import get_client_ip, validar_ip, obtener_lag_replicacion
from .services import autenticar_usuario_bd, buscar_logs_clientes_bd, obtener_estado_replicacion_bd, registrar_cliente_bd, registrar_cuenta_bd, obtener_sugerencias_clientes_bd, obtener_ids_clientes_bd, obtener_cliente_por_id_bd, modificar_cliente_bd, obtener_cuenta_por_id_bd, obtener_ids_cuentas_bd, modificar_cuenta_bd, buscar_clientes_bd, buscar_cuentas_bd, eliminar_cliente_bd, eliminar_cuenta_bd, buscar_logs_cuentas_bd, registrar_usuario_db

def rol_requerido(roles):
    def decorador(vista_funcion):
        @wraps(vista_funcion)
        def wrapper(request, *args, **kwargs):
            if "id_usuario" not in request.session:
                return redirect('/login/?mensaje=Tu sesión ha expirado por inactividad.')
            tipo = request.session.get('tipo')
            
            if tipo not in roles:
                return redirect('acceso_denegado')
            return vista_funcion(request, *args, **kwargs)
        return wrapper
    return decorador

@rol_requerido(['Master', 'Programador', 'Sistema', 'Lector', 'API'])
@never_cache
def home(request):
    if not request.session.get('usuario'):
        return redirect('/login/')
    
    usuario = request.session.get('usuario')
    tipo = request.session.get('tipo')
    last_login_utc = request.session.get('last_login')
    total_login = request.session.get('total_login')

    contexto = {
        'usuario': usuario,
        'tipo': tipo,
        'last_login': last_login_utc,
        'total_login': total_login,
    }
    return render(request, 'base/home.html', contexto)


@require_POST
def logout(request):
    print("Logout")
    request.session.flush()
    return redirect('/login/')

@csrf_exempt
@never_cache
def login(request):
    mensaje = request.GET.get('mensaje')

    if request.method == 'POST':
        request.session.flush()
        print('Datos recibidos de POST: ', request.POST)
        form = LoginForm(request.POST)

        if form.is_valid():
            print("[DEBUG] El formulario es VÁLIDO.")
            correo = form.cleaned_data['CorreoElectronico']
            password = form.cleaned_data['Pass']
            zona_horaria = form.cleaned_data.get('zona_horaria', 'UTC')
            ip_cliente = get_client_ip(request)

            try:
                resultado_json = autenticar_usuario_bd(correo, password, ip_cliente, zona_horaria)
            except ValueError:
                return HttpResponse("Error de respuesta del servidor")

            if resultado_json.get("Estado") == 'Log in exitoso':
                request.session['usuario'] = resultado_json.get("Usuario")
                request.session['tipo'] = resultado_json.get("Tipo")
                request.session['id_usuario'] = resultado_json.get("IDUsuario")

                last_login_raw = resultado_json.get("Last_Login")
                request.session['last_login'] = str(last_login_raw).split('.')[0] if last_login_raw else 'Nunca'
                request.session['total_login'] = resultado_json.get('Total_Login')

                messages.success(request, "Inicio de sesión exitoso! Bienvenido/a")
                return redirect('home')
            else:
                return render(request, 'auth/login.html', {
                    'error': resultado_json.get("Estado"),
                    'estado': 'login fallido',
                    'mensaje': mensaje
                })
        else:
            print("[DEBUG] El formulario es INVÁLIDO. Errores:", form.errors)
            error_list = list(form.errors.values())
            first_error = error_list[0][0] if error_list else 'Error en los datos.'
            
            return render(request, 'auth/login.html', {
                'error' : first_error,
                'estado' : 'datos_invalidos',
                'mensaje' : mensaje
            })

    return render(request, 'auth/login.html', { 'mensaje': mensaje })

@never_cache
@rol_requerido(['Master'])
def insertar_menu(request):
    return render(request, 'insertar_menu.html')

@rol_requerido(['Master'])
@never_cache
def agregar_cliente(request):
    error = None
    datos = []

    if request.method == 'POST':
        form = ClientForm(request.POST)
        
        if form.is_valid():
            datos_limpios = form.cleaned_data
            created_by = request.session.get('id_usuario')
            ip = get_client_ip(request)
        
            if not created_by:
                return redirect('/login/?mensaje=Tu sesión ha expirado.')
            
            try:
                registrar_cliente_bd(
                    datos_limpios['nombre'],
                    datos_limpios['apellido'],
                    datos_limpios['telefono'],
                    datos_limpios['correo'],
                    datos_limpios['direccion'],
                    int(created_by),
                    datos_limpios.get('zona_horaria', 'UTC'),
                    ip
                )
                
                messages.success(request, "Cliente agregado correctamente.")
                
                return redirect('/agregar_cliente/')
            
            except Exception as e:
                print(f"[ERROR] Error al agregar al cliente: {e}")
                messages.error(request, "Ocurrió un error inesperado al guardar en la base de datos.")
            
        else:
            error_list = list(form.errors.values())
            error = error_list[0][0] if error_list else 'Revisa los datos ingresados.'
            
    elif request.method == 'GET' and any(request.GET.get(param) for param in ['nombre', 'apellido', 'telefono', 'correo']):
        nombre_buscar = request.GET.get('nombre', '').strip() or None
        apellido_buscar = request.GET.get('apellido', '').strip() or None
        telefono_buscar = request.GET.get('telefono', '').strip() or None
        correo_buscar = request.GET.get('correo', '').strip() or None
        
    return render(request, 'clientes/agregar_cliente.html', {
        'usuario': request.session.get('usuario'),
        'tipo': request.session.get('tipo'),
        'error': error,
        'datos': datos,
    })

@rol_requerido(['Master'])
@never_cache
def agregar_cuenta(request):
    if request.method == "POST":
        form = CuentaForm(request.POST)
        
        if form.is_valid():
            datos = form.cleaned_data
            created_by = request.session.get('id_usuario')
            ip_cliente = get_client_ip(request)
            
            if not validar_ip(ip_cliente):
                messages.error(request, "IP del cliente no válida.")
            else:
                try:
                    registrar_cuenta_bd(
                        id_cliente=datos['id_cliente'],
                        estado=datos['estado'],
                        created_by=created_by,
                        ip_cliente=ip_cliente,
                        zona_horaria=datos.get('zona_horaria', 'UTC')
                    )
                    messages.success(request, "Cuenta agregada correctamente.")
                    return redirect('/agregar_cuenta/')
                
                except ValueError as ve:
                    messages.error(request, str(ve))
                except Exception as e:
                    print(f"[ERROR] Error al agregar cuenta: {e}")
                    messages.error(request, "Ocurrió un error inesperado al guardar en la base de datos.")
        else:
            error_list = list(form.errors.values())
            primer_error = error_list[0][0] if error_list else 'Revisa los datos ingresados.'
            messages.error(request, primer_error)
        
    sugerencias_clientes = obtener_sugerencias_clientes_bd()
    
    return render(request, 'cuentas/agregar_cuenta.html', {
        'usuario' : request.session.get('usuario'),
        'tipo' : request.session.get('tipo'),
        'sugerencias_clientes' : sugerencias_clientes,
    })

@never_cache
@rol_requerido(['Master'])
def modificar_menu(request):
    return render(request, 'menus/modificar_menu.html')

@never_cache
@rol_requerido(['Master'])
def modificar_cliente(request, id=None):
    cliente = None
    clientes_ids = obtener_ids_clientes_bd()
    
    id_cliente = id or request.GET.get('id_cliente') or request.POST.get('id_cliente')
    
    if request.method == 'POST':
        if 'buscar' in request.POST:
            cliente = obtener_cliente_por_id_bd(id_cliente)
            if not cliente:
                messages.error(request, f"No se encontró el cliente con ID {id_cliente}.")
                
        elif 'modificar' in request.POST:
            form = ModiciarClienteForm(request.POST)
            
            if form.is_valid():
                datos = form.cleaned_data
                modified_by = request.session.get('id_usuario')
                ip = get_client_ip(request)
                
                if not modified_by:
                    return redirect('/login/?mensaje=Tu sesión ha expirado.')
                
                try:
                    modificar_cliente_bd(
                        id_cliente=datos['id_cliente'],
                        nombre=datos['nombre'],
                        apellido=datos['apellido'],
                        telefono=datos['telefono'],
                        correo=datos['correo'],
                        direccion=datos['direccion'],
                        modified_by=modified_by,
                        deleted=datos.get('deleted', False),
                        zona_horaria=datos.get('zona_horaria', 'UTC'),
                        ip_cliente=ip
                    )
                    messages.success(request, "Cliente modificado correctamente.")
                    
                    return redirect(f'/modificar_cliente/{datos["id_cliente"]}/')
                except Exception as e:
                    print(f"[ERROR] Error al modificar cliente: {e}")
                    messages.error(request, "Ocurrió un error inesperado al guardar en la base de datos.")
            else:
                error_list = list(form.errors.values())
                messages.warning(request, error_list[0][0] if error_list else 'Revisa los datos ingresados.')
                cliente = obtener_cliente_por_id_bd(id_cliente)
            
    if id_cliente and not cliente and request.method != 'POST':
        cliente = obtener_cliente_por_id_bd(id_cliente)
        if not cliente:
            messages.error(request, f"No se encontró el cliente con ID {id_cliente}.")
            
    return render(request, 'clientes/modificar_cliente.html', {
        'usuario' : request.session.get('usuario'),
        'tipo' : request.session.get('tipo'),
        'cliente' : cliente,
        'clientes_ids' : clientes_ids,
    })

@never_cache
@rol_requerido(['Master'])
def modificar_cuenta(request, id=None):
    cuenta = None
    lista_cuentas = obtener_ids_cuentas_bd()
    
    id_cuenta = id or request.GET.get('id_cuenta') or request.POST.get('id_cuenta')
    
    if request.method == 'POST':
        if 'buscar' in request.POST:
            if not id_cuenta or not str(id_cuenta).isdigit():
                messages.error(request, "ID de cuenta inválido.")
            else:
                cuenta = obtener_cuenta_por_id_bd(id_cuenta)
                if not cuenta:
                    messages.error(request, f"No se encontró la cuenta con ID {id_cuenta}.")
                    
        elif 'modificar' in request.POST:
            form = ModificarCuentaForm(request.POST)
            modified_by = request.session.get('id_usuario')
            ip = get_client_ip(request)
            
            if not modified_by:
                return redirect('/login/?mensaje=Tu sesión ha expirado.')
            
            if form.is_valid():
                datos = form.cleaned_data
                try:
                    modificar_cuenta_bd(
                        id_cuenta=datos['id_cliente'],
                        id_cliente=datos['id_cliente'],
                        saldo=datos['saldo'],
                        estado=datos['estado'],
                        modified_by=int(modified_by),
                        deleted=datos['deleted'],
                        zona_horaria=datos.get('zona_horaria', 'UTC'),
                        ip_cliente=ip
                    )
                    messages.success(request, "Cuenta modificada correctamente.")
                    
                    return redirect(f'/modificar_cuenta/{datos["id_cliente"]}/')
                except Exception as e:
                    print(f"[ERROR] Error al modificar cuenta: {e}")
                    messages.error(request, "Ocurrió un error inesperado al guardar en la base de datos.")
            else:
                error_list = list(form.errors.values())
                messages.warning(request, error_list[0][0] if error_list else 'Revisa los datos ingresados.')
                cuenta = obtener_cuenta_por_id_bd(id_cuenta)
    if id_cuenta and not cuenta and request.method != 'POST':
        if str(id_cuenta).isdigit():
            cuenta = obtener_cuenta_por_id_bd(id_cuenta)
            if not cuenta:
                messages.error(request, f"No se encontró la cuenta con ID {id_cuenta}.")
        else:
            messages.error(request, "ID de cuenta inválido.")
        
    return render(request, 'cuentas/modificar_cuenta.html', {
        'cuenta' : cuenta,
        'cuentas' : lista_cuentas,
        'usuario' : request.session.get('usuario'),
        'tipo' : request.session.get('tipo'),
    })

@never_cache
@rol_requerido(['Master', 'Lector'])
def consultas_menu(request):
    return render(request, 'menus/consultas_menu.html')

@rol_requerido(['Master','Lector'])
@never_cache
def consultas_clientes(request):
    datos = []
    
    data = request.POST if request.method == 'POST' else request.GET
    form = FiltroClienteForm(data)
    
    campos = {
        'nombre_completo' : None,
        'telefono' : None,
        'correo' : None,
        'direccion' : None,
        'registro' : None
    }
    
    if form.is_valid():
        campos = {
            'nombre_completo' : form.cleaned_data.get('nombre_completo') or None,
            'telefono' : form.cleaned_data.get('telefono') or None,
            'correo' : form.cleaned_data.get('correo') or None,
            'direccion' : form.cleaned_data.get('direccion') or None,
            'registro' : form.cleaned_data.get('registro') or None
        }
        
        if request.method == 'POST' or any(campos.values()):
            try:
                datos = buscar_clientes_bd(
                    campos['nombre_completo'],
                    campos['telefono'],
                    campos['correo'],
                    campos['direccion'],
                    campos['registro']
                )
                
                if not datos and any(campos.values()):
                    messages.info(request, "No se encontraron clientes que coincidan con los criterios de búsqueda.")
                    
            except Exception as e:
                print(f"[ERROR] Error en consulta de clientes: {e}")
                messages.error(request, 'Ocurrio un error inesperado alrealizar la búsqueda. Por favor, intenta nuevamente.')
    if request.GET.get('deleted') == '1':
        messages.success(request, "Cliente eliminado correctamente.")
    
    return render(request, 'clientes/consultas_clientes.html', {
        'usuario' : request.session.get('usuario'),
        'tipo' : request.session.get('tipo'),
        'datos' : datos,
        **campos
    })

@rol_requerido(['Master', 'Programador', 'Lector'])
@never_cache
def consultas_cuentas(request):
    datos = []

    data = request.POST if request.method == 'POST' else request.GET
    form = FiltroCuentasForm(data)
    
    campos = {
        'id_cuenta': None,
        'nombre_completo': None,
        'telefono': None,
        'correo': None,
    }
    
    if form.is_valid():
        campos = {
            'id_cuenta': form.cleaned_data.get('id_cuenta') or None,
            'nombre_completo': form.cleaned_data.get('nombre_completo') or None,
            'telefono': form.cleaned_data.get('telefono') or None,
            'correo': form.cleaned_data.get('correo') or None,
        }
        
        if request.method == 'POST' or any(campos.values()):
            try:
                datos = buscar_cuentas_bd(
                    campos['id_cuenta'],
                    campos['nombre_completo'],
                    campos['telefono'],
                    campos['correo']
                )
                
                if not datos and any(campos.values()):
                    messages.info(request, "No se encontraron cuentas que coincidan con los criterios de búsqueda.")
            
            except Exception:
                messages.error(request, "Ocurrió un error inesperado al realizar la búsqueda. Por favor, intenta nuevamente.")
                
    if request.GET.get('deleted') == '1':
        messages.success(request, "Cuenta eliminada correctamente.")
        
    return render(request, 'cuentas/consultas_cuentas.html', {
        'usuario': request.session.get('usuario'),
        'tipo': request.session.get('tipo'),
        'datos': datos,
        **campos
    })

@csrf_protect
@rol_requerido(['Master'])
def eliminar_cliente(request, id):
    if request.method == 'POST':
        modified_by = request.session.get('id_usuario')
        zona_horaria = request.session.get('zona_horaria', 'UTC')
        ip_cliente = get_client_ip(request)
        
        if not modified_by:
            messages.error(request, "Tu sesión ha expirado o es inválida.")
            return redirect('/login/')
        
        try:
            eliminar_cliente_bd(
                id_cliente=id,
                modified_by=int(modified_by),
                zona_horaria=zona_horaria,
                ip_cliente=ip_cliente
            )
            
            messages.success(request, "Cliente eliminado correctamente.")
            
        except Exception as e:
            print(f"[ERROR] Error al eliminar cliente: {e}")
            messages.error(request, "Ocurrió un error inesperado al eliminar el cliente.")
            
    return redirect('consultas_clientes')

@csrf_protect
@rol_requerido(['Master'])
def eliminar_cuenta(request, id_cuenta):
    if request.method == 'POST':
        modified_by = request.session.get('id_usuario')
        zona_horaria = request.session.get('zona_horaria', 'UTC')
        ip_cliente = get_client_ip(request)
        
        if not modified_by:
            messages.error(request, "Tu sesión ha expirado o es inválida.")
            return redirect('/login/')
        
        try:
            eliminar_cuenta_bd(
                id_cuenta=id_cuenta,
                modified_by=int(modified_by),
                zona_horaria=zona_horaria,
                ip_cliente=ip_cliente
            )
            
            messages.success(request, "Cuenta eliminada correctamente.")
        
        except Exception as e:
            print(f"[ERROR] Error al eliminar cuenta: {e}")
            messages.error(request, "Ocurrió un error inesperado al eliminar la cuenta.")
        
    return redirect('consultas_cuentas')

@rol_requerido(["Sistema"])
@never_cache
def consultas_logs_menu(request):
    return render(request, "consultas_logs_menu.html")

@rol_requerido(['Sistema'])
@never_cache
def consultar_logs_clientes(request):
    resultados = []
    busqueda_realizada = False

    if request.GET:
        form = FiltroLogsForm(request.GET)
        
        if form.is_valid():
            datos = form.cleaned_data
            fecha_inicio = datos.get('fecha_inicio')
            fecha_fin = datos.get('fecha_fin')
            
            if fecha_inicio and fecha_fin:
                busqueda_realizada = True
                try:
                    resultados = buscar_logs_clientes_bd(
                        fecha_inicio,
                        fecha_fin,
                        datos.get('tipo_operacion', '')
                    )
                    
                    if not resultados:
                        messages.info(request, 'No se encontraron registros que coincidan con los criterios de búsqueda.')
                except Exception as e:
                    print(f"[ERROR] Error al buscar logs de clientes: {e}")
                    messages.error(request, 'Ocurrió un error inesperado al realizar la búsqueda. Por favor, intenta nuevamente.')
            else:
                for error in form.errors.values():
                    messages.warning(request, error[0])

    return render(request, "auditoria/consultar_logs_clientes.html", {
        "resultados": resultados,
        "fecha_inicio": request.GET.get('fecha_inicio', ''),
        "fecha_fin": request.GET.get('fecha_fin', ''),
        "tipo_operacion": request.GET.get('tipo_operacion', ''),
        "busqueda_realizada": busqueda_realizada,
    })

@rol_requerido(["Sistema"])
@never_cache
def consultar_logs_cuentas(request):
    resultados = []
    busqueda_realizada = False

    if request.GET:
        form = FiltroLogsForm(request.GET)
        
        if form.is_valid():
            datos = form.cleaned_data
            fecha_inicio = datos.get('fecha_inicio')
            fecha_fin = datos.get('fecha_fin')
            
            if fecha_inicio and fecha_fin:
                busqueda_realizada = True
                try:
                    resultados = buscar_logs_cuentas_bd(
                        fecha_inicio,
                        fecha_fin,
                        datos.get('tipo_operacion', '')
                    )
                    
                    if not resultados:
                        messages.info(request, 'No se encontraron registros que coincidan con los criterios de búsqueda.')
                except Exception as e:
                    messages.error(request, 'Ocurrió un error inesperado al realizar la búsqueda. Por favor, intenta nuevamente.')
                    
        else:
            for error in form.errors.values():
                messages.warning(request, error[0])

    return render(request, "auditoria/consultar_logs_cuentas.html", {
        "resultados": resultados,
        "fecha_inicio": request.GET.get('fecha_inicio', ''),
        "fecha_fin": request.GET.get('fecha_fin', ''),
        "tipo_operacion": request.GET.get('tipo_operacion', ''),
    })

@rol_requerido(["Master"])
@never_cache
def signup_step1(request):
    if request.method == 'POST':
        form = SignupStep1Form(request.POST)
        
        if form.is_valid():
            datos = form.cleaned_data
            ip = get_client_ip(request)
            
            request.session['registro'] = {
                'NombreDeUsuario': datos['NombreDeUsuario'],
                'CorreoElectronico': datos['CorreoElectronico'],
                'Pass': datos['Pass'],
                'ZonaHoraria': datos.get('zona_horaria', 'UTC'),
                'IPCliente': ip,
            }
            
            return redirect('signup_step2')
        else:
            error_list = list(form.errors.values())
            messages.warning(request, error_list[0][0] if error_list else 'Revisa los datos ingresados.')
    return render(request, 'auth/signup_step1.html')

@rol_requerido(["Master"])
@never_cache
def signup_step2(request):
    data_step1 = request.session.get('registro')
    if not data_step1:
        messages.error(request, "No se encontraron datos de registro. Por favor, completa el paso 1.")
        return redirect('signup_step1')
    
    if request.method == 'POST':
        form = SignupStep2Form(request.POST)
        created_by = request.session.get('id_usuario')
        
        if not created_by:
            return HttpResponseForbidden('Sesión no válida')
        
        if form.is_valid():
            datos = form.cleaned_data
            try:
                registrar_usuario_db(
                    nombre_usuario=data_step1['NombreDeUsuario'],
                    nombre_completo=datos['NombreCompleto'],
                    correo=data_step1['CorreoElectronico'],
                    telefono=datos['Telefono'],
                    password=data_step1['Pass'],
                    rol=datos['Rol'],
                    estado=datos['Estado'],
                    created_by=int(created_by),
                    zona=data_step1['ZonaHoraria'],
                    ip=data_step1['IPCliente']
                )
                
                del request.session['registro']
                messages.success(request, "Usuario registrado correctamente.")
                return redirect('home')
            
            except Exception as e:
                print(f"[ERROR] Error al registrar usuario: {e}")
                messages.error(request, "Ocurrió un error inesperado al guardar en la base de datos.")
        
        else:
            error_list = list(form.errors.values())
            messages.warning(request, error_list[0][0] if error_list else 'Revisa los datos ingresados.')
            
    return render(request, 'auth/signup_step2.html', {
        'roles' : [rol[0] for rol in SignupStep2Form.ROLES],
        'estados' : [estado[0] for estado in SignupStep2Form.ESTADOS],
    })

@never_cache
@rol_requerido(['Master', 'Sistema'])
def ver_lag_replicacion(request):
    estado = obtener_estado_replicacion_bd()
    
    lag_mostrar = estado.get('seconds_behind')
    if lag_mostrar is None:
        lag_mostrar = 'Desconocido / Sin replicación'
        
    return render(request, 'lag_replicacion.html', {
        'lag': lag_mostrar,
        'activa' : estado.get('replicacion_activa'),
        'es_simulacion' : estado.get('modo_debug')
    })

@never_cache
@rol_requerido(['Master', 'Sistema'])
def estado_replicacion(request):
    estado = obtener_estado_replicacion_bd()
    return JsonResponse(estado)

def estado_sesion(request):
    if request.session.get('usuario'):
        return JsonResponse({
            'estado': 'activo',
            'usuario': request.session.get('usuario'),
            'tipo': request.session.get('tipo'),
        })
    else:
        return JsonResponse({'estado': 'inactivo'})

def acceso_denegado(request):
    mensaje = "No tienes permisos para acceder a esta página."
    destino = "home"

    if not request.session.get('usuario'):
        mensaje = "Debes iniciar sesión para acceder a esta página."
        destino = "/login/"

    return render(request, 'base/403.html', {
        'mensaje': mensaje,
        'volver_a': destino
    })
