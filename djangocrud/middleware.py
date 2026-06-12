from django.db import connections, OperationalError
from django.shortcuts import render

class ManejoErrorConexionDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            connections['default'].cursor()
        except OperationalError:
            return render(request, 'base/error_db.html', status=503)
        
        response = self.get_response(request)
        return response
