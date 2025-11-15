from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    # puedes agregar más campos si quieres
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.username
