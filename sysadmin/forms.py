from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

OPERACIONES_CHOICES = [
    ('', 'Todas'),
    ('crear', 'Crear'),
    ('editar', 'Editar'),
    ('eliminar', 'Eliminar'),
]

class LoginForm(forms.Form):
    CorreoElectronico = forms.EmailField(
        max_length=100,
        required=True,
        error_messages={
            'required' : 'Correo y contraseña son obligatorios.',
            'invalid' : 'El correo ingresado no es válido.',
            'max_length' : 'La longitud del correo es inválida.'
        }
    )
    
    Pass = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.PasswordInput,
        error_messages={
            'required': 'Correo y contraseña son obligatorios.',
            'max_length': 'La longitud de la contraseña es inválida.'
        }
    )
    
    zona_horaria = forms.CharField(required=False, initial='UTC')
    
class ClientForm(forms.Form):
    nombre = forms.CharField(
        validators=[RegexValidator(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", "Nombre inválido. Usa solo letras y espacios.")],
        required=True
    )
    apellido = forms.CharField(
        validators=[RegexValidator(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", "Apellido inválido. Usa solo letras y espacios.")]
    )
    telefono = forms.CharField(
        validators=[RegexValidator(r"^\d{10}$", "El teléfono debe tener exactamente 10 dígitos.")],
        required=True
    )
    correo = forms.EmailField(
        error_messages={'invalid': 'Correo electrónico no válido.'},
        required=True
    )
    direccion = forms.CharField(
        max_length=255, 
        error_messages={'max_length': 'La dirección es demasiado larga (máx. 255 caracteres).'},
        required=True
    )
    zona_horaria = forms.CharField(required=False, initial='UTC')

class CuentaForm(forms.Form):
    ESTADOS = [
        ('Activa', 'Activa'),
        ('Suspendida', 'Suspendida'),
    ]
    
    id_cliente = forms.IntegerField(
        required=True,
        error_messages={
            'required': 'El ID del cliente es obligatorio.',
            'invalid': 'El ID del cliente debe ser un número entero.'
        }
    )
    estado = forms.ChoiceField(
        choices=ESTADOS,
        required=True,
        error_messages={
            'required': 'El estado de la cuenta es obligatorio.',
            'invalid_choice': 'Estado de cuenta no válido.'
        }
    )
    zona_horaria = forms.CharField(
        max_length=100,
        required=True,
        initial='UTC',
        error_messages={'max_length': 'La zona horaria es demasiado larga (máx. 100 caracteres).'}
    )

class ModiciarClienteForm(ClientForm):
    id_cliente = forms.IntegerField(required=True)
    deleted = forms.BooleanField(required=False, initial=False)

class ModificarCuentaForm(CuentaForm):
    id_cuenta = forms.IntegerField(
        required=True,
        error_messages={
            'required': 'El ID de la cuenta es obligatorio.',
            'invalid': 'El ID de la cuenta debe ser un número entero.'
        }
    )
    saldo = forms.DecimalField(
        required=True,
        decimal_places=2,
        error_messages={
            'required': 'El saldo es obligatorio.',
            'invalid': 'El saldo debe ser un número decimal válido.'
        }
    )
    deleted = forms.BooleanField(required=False, initial=False)

class FiltroClienteForm(forms.Form):
    nombre_completo = forms.CharField(required=False)
    telefono = forms.CharField(required=False)
    correo = forms.CharField(required=False)
    direccion = forms.CharField(required=False)
    registro = forms.CharField(required=False)

class FiltroCuentasForm(forms.Form):
    id_cuenta = forms.CharField(required=False)
    nombre_completo = forms.CharField(required=False)
    telefono = forms.CharField(required=False)
    correo = forms.CharField(required=False)

class FiltroLogsForm(forms.Form):
    FORMATOS_ACEPTADOS = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
    fecha_inicio = forms.DateField(input_formats=FORMATOS_ACEPTADOS, required=True)
    fecha_fin = forms.DateField(input_formats=FORMATOS_ACEPTADOS, required=True)
    
    OPCIONES_TIPO = [
        ('todos', '-- Todos --'),
        ('insert', 'Insert'),
        ('update', 'Update'),
        ('delete', 'Delete')
    ]
    
    tipo_operacion = forms.ChoiceField(choices=OPCIONES_TIPO, required=False, initial='todos')
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise forms.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        
        return cleaned_data

class SignupStep1Form(forms.Form):
    NombreDeUsuario = forms.CharField(max_length=150, required=True)
    CorreoElectronico = forms.EmailField(required=True)
    Pass = forms.CharField(widget=forms.PasswordInput(), required=True)
    zona_horaria = forms.CharField(max_length=100, required=True)

class SignupStep2Form(forms.Form):
    ROLES = [
        ('Master', 'Master'), 
        ('Sistema', 'Sistema'), 
        ('Lector', 'Lector')
    ]
    ESTADOS = [
        ('Activo', 'Activo'), 
        ('Inactivo', 'Inactivo')
    ]
    
    NombreCompleto = forms.CharField(max_length=255, required=True)
    Telefono = forms.CharField(max_length=20, required=True)
    Rol = forms.ChoiceField(choices=ROLES, required=True)
    Estado = forms.ChoiceField(choices=ESTADOS, required=True)
