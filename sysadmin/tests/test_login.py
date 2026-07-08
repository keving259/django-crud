from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse

class LoginTests(TestCase):
    databases = {'default', 'replica'}
    def setUp(self):
        self.correo = 'master@test.com'
        self.zona_horaria = 'America/Mexico_City'
    
    
    
    @patch('sysadmin.views.autenticar_usuario_bd')
    def test_login_exitoso(self, mock_auth):
        mock_auth.return_value = {
            "Estado": "Log in exitoso",
            "Usuario": "Master",
            "Tipo": "Master",
            "IDUsuario": 1,
            "Last_Login": None,
            "Total_Login": 5
        }

        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico': self.correo,
                'Pass': '123456',
                'zona_horaria': self.zona_horaria
            }
        )

        self.assertRedirects(response, reverse('home'))

        session = self.client.session

        self.assertEqual(session['usuario'], 'Master')
        self.assertEqual(session['tipo'], 'Master')
        self.assertEqual(session['id_usuario'], 1)
        
    @patch('sysadmin.views.autenticar_usuario_bd')
    def test_login_fallido(self, mock_auth):
        mock_auth.return_value = {
            'Estado' : 'Contraseña incorrecta'
        }
        
        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico' : self.correo,
                'Pass' : 'incorrecta',
                'zona_horaria' : self.zona_horaria
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Contraseña incorrecta'
        )
    
    
    
    @patch('sysadmin.views.autenticar_usuario_bd')
    def test_usuario_inexistente(self, mock_auth):
        mock_auth.return_value = {
            'Estado' : 'El correo ingresado no es válido.'
        }
        
        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico' : 'Inexistente',
                'Pass' : '123456',
                'zona_horaria' : self.zona_horaria
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El correo ingresado no es válido.'
        )
        
    
    
    def test_correo_vacio(self):
        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico' : '',
                'Pass' : '123456',
                'zona_horaria' : self.zona_horaria
            }
        )

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Correo y contraseña son obligatorios.'
        )
        
    
    
    def test_password_vacia(self):
        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico' : self.correo,
                'Pass' : '',
                'zona_horaria' : self.zona_horaria
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'Correo y contraseña son obligatorios.'
        )

    
    
    def test_correo_invalido(self):
        response = self.client.post(
            reverse('login'),
            {
                'CorreoElectronico': 'correo_invalido',
                'Pass': '123456',
                'zona_horaria': self.zona_horaria
            }
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(
            response,
            'El correo ingresado no es válido.'
        )