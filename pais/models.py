from django.db import models

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
