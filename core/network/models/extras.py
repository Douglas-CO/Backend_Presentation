from django.db import models
from django.forms import model_to_dict


class OLTCoordinateTable(models.Model):
    slot_id = models.IntegerField()
    port_pon_id = models.IntegerField()
    coordinate = models.CharField(max_length=10)

    def __str__(self):
        return self.coordinate

    def as_dict(self):
        item = model_to_dict(self, exclude=['id'])
        return item

    class Meta:
        verbose_name = 'Tabla de coordenada OLT'
        verbose_name_plural = 'Tabla de coordenadas OLT'
        default_permissions = ()


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def has_changes(self):
        if self.pk:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                fields_to_check = [field.name for field in self._meta.fields if field.name != 'id']
                return any(getattr(old_instance, field) != getattr(self, field) for field in fields_to_check)
            except:
                return True
        return True
