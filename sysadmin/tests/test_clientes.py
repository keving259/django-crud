from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

class ClienteTests(TestCase):
    databases = {'default', 'replica'}
    def setUp(self):
        session = self.client.session
        session['id_usuario'] = 1
        session['usuario'] = 'Master'
        session['tipo'] = 'Master'
        session.save()
        
    def test_sesion_existe(self):
        self.assertEqual(
            self.client.session['id_usuario'],
                1
            )
        
        self.assertEqual(
            self.client.session['tipo'],
            'Master'
        )
        
    @patch('sysadmin.views.registrar_cliente_bd')
    def test_agregar_cliente_exitoso(self, mock_registrar):
        
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': 'John',
                'apellido': 'Doe',
                'telefono': '6181234567',
                'correo': 'master@test.com',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }, follow=False
        )
        
        self.assertRedirects(
            response,
            reverse('agregar_cliente')
        )
        
        mock_registrar.assert_called_once()
        
        
    def test_agregar_cliente_nombre_vacio(self):
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': '',
                'apellido': 'Doe',
                'telefono': '6181234567',
                'correo': 'master@test.com',
                'direccion': 'av 123'
            }
        )
        
        self.assertEqual(response.status_code, 200)
    
    
        
    @patch('sysadmin.views.buscar_clientes_bd')
    def test_busqueda_cliente_inexistente(self, mock_buscar):
        mock_buscar.return_value = []
        
        response = self.client.get(
            reverse('consultas_clientes'),
            {
                'nombre_completo': 'NoExiste'
            }
        )
        
        self.assertEqual(response.status_code, 200)
    
    
    
    @patch('sysadmin.views.modificar_cliente_bd')
    @patch('sysadmin.views.obtener_cliente_por_id_bd')
    def test_modificar_cliente_exitoso(
        self,
        mock_obtener,
        mock_modificar
    ):
        
        mock_obtener.return_value = {
            'IDCliente': 1,
            'Nombre': 'John'
        }
        
        response = self.client.post(
            reverse('modificar_cliente'),
            {
                'modificar': True,
                'id_cliente': 1,
                'nombre': 'John',
                'apellido': 'Doe',
                'telefono': '6181234567',
                'correo': 'nuevo@test.com',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }
        )
        
        mock_modificar.assert_called_once()
        
    
    
    @patch('sysadmin.views.eliminar_cliente_bd')
    def test_eliminar_cliente(self, mock_eliminar):
        session = self.client.session
        session['id_usuario'] = 1
        session['zona_horaria'] = 'America/Mexico_City'
        session.save()
        
        response = self.client.post(
            reverse('eliminar_cliente', args=[1])
        )
        
        mock_eliminar.assert_called_once()
        
        self.assertRedirects(
            response,
            reverse('consultas_clientes')
        )
    
    
    def test_nombre_invalido(self):
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': 'John123',
                'apellido': 'Doe',
                'telefono': '6181234567',
                'correo': 'master@test.com',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Nombre inválido. Usa solo letras y espacios.'
        )
        
        
    def test_apellido_invalido(self):
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': 'John',
                'apellido': 'Doe123',
                'telefono': '6181234567',
                'correo': 'master@test.com',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Apellido inválido. Usa solo letras y espacios.'
        )
        
        
    
    def test_telefono_invalido(self):
        
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': 'John',
                'apellido': 'Doe',
                'telefono': '123',
                'correo': 'master@test.com',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El teléfono debe tener exactamente 10 dígitos.'
        )
    
    
    
    def test_correo_invalido(self):
        response = self.client.post(
            reverse('agregar_cliente'),
            {
                'nombre': 'John',
                'apellido': 'Doe',
                'telefono': '6181234567',
                'correo': 'correo_invalido',
                'direccion': 'av 123',
                'zona_horaria': 'America/Mexico_City'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Correo electrónico no válido.'
        )
