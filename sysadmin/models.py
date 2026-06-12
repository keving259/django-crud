from django.db import models

from django.contrib.auth.models import User

class Log(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    operacion = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.fecha} - {self.usuario} - {self.operacion}"
