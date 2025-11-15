from django.db import models
from pais.models import Pais

class Provincia(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50)
    state = models.BooleanField(default=True)

    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="provincias")

    def __str__(self):
        return self.nombre
