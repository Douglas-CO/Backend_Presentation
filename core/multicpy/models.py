# core/multicpy/models.py
from django.db import models


class Scheme(models.Model):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
