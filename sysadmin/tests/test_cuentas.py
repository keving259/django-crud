from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse


class CuentaTests(TestCase):
    databases = {'default', 'replica'}
    def setUp(self):
        session = self.client.session
        session['id_usuario'] = 1
        session['usuario'] = 'Master'
        session['tipo'] = 'Master'
        session.save()
        
        self.datos_validos = {
            'id_cliente': 1,
            'estado': 'Activa',
            'zona_horaria': 'America/Mexico_City'
        }
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    @patch('sysadmin.views.registrar_cuenta_bd')
    @patch('sysadmin.views.validar_ip')
    def test_agregar_cuenta_exitosa(
        self,
        mock_validar_ip,
        mock_registrar,
        mock_sugerencias
    ):
        mock_validar_ip.return_value = True
        mock_sugerencias.return_value = []
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            self.datos_validos
        )
        
        self.assertRedirects(
            response,
            reverse('agregar_cuenta')
        )
        
        mock_registrar.assert_called_once()
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    @patch('sysadmin.views.validar_ip')
    def test_ip_invalida(
        self,
        mock_validar_ip,
        mock_sugerencias
    ):
        mock_validar_ip.return_value = False
        mock_sugerencias.return_value = []
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            self.datos_validos
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'IP del cliente no válida.'
        )
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    @patch('sysadmin.views.registrar_cuenta_bd')
    @patch('sysadmin.views.validar_ip')
    def test_cliente_inexistente(
        self,
        mock_validar_ip,
        mock_registrar,
        mock_sugerencias
    ):
        mock_validar_ip.return_value = True
        mock_sugerencias.return_value = []
        
        mock_registrar.side_effect = ValueError(
            'El cliente con ID 999 no existe.'
        )
        
        datos = self.datos_validos.copy()
        datos['id_cliente'] = 999
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            datos
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El cliente con ID 999 no existe.'
        )
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    def test_estado_invalido(
        self,
        mock_sugerencias
    ):
        mock_sugerencias.return_value = []
        
        datos = self.datos_validos.copy()
        datos['estado'] = 'Eliminada'
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            datos
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Estado de cuenta no válido.'
        )
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    def test_id_cliente_vacio(
        self,
        mock_sugerencias
    ):
        mock_sugerencias.return_value = []
        
        datos = self.datos_validos.copy()
        datos['id_cliente'] = ''
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            datos
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El ID del cliente es obligatorio.'
        )
        
    @patch('sysadmin.views.obtener_sugerencias_clientes_bd')
    def test_id_cliente_no_numerico(
        self,
        mock_sugerencias
    ):
        mock_sugerencias.return_value = []
        
        datos = self.datos_validos.copy()
        datos['id_cliente'] = 'abc'
        
        response = self.client.post(
            reverse('agregar_cuenta'),
            datos
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El ID del cliente debe ser un número entero.'
        )
