import unicodedata
from datetime import datetime
from io import BytesIO

from barcode import Gs1_128, writer
from django.core.files.base import ContentFile
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse_lazy
from unidecode import unidecode

from config import settings
from core.billing.choices import VOUCHER_TYPE, VOUCHER_STAGE
from core.multicpy.choices import ENVIRONMENT_TYPE
from core.security.fields import CustomImageField


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True,
                            help_text='Ingrese un nombre', verbose_name='Nombre')

    def __str__(self):
        return self.name

    def as_dict(self):
        item = model_to_dict(self)
        return item

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['id']


class Product(models.Model):
    name = models.CharField(
        max_length=150, help_text='Ingrese un nombre', verbose_name='Nombre')
    code = models.CharField(max_length=20, unique=True,
                            help_text='Ingrese un código', verbose_name='Código')
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='Categoría')
    has_tax = models.BooleanField(
        default=True, verbose_name='¿Tiene impuesto?')
    price = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00, verbose_name='Precio')
    barcode = CustomImageField(
        null=True, blank=True, verbose_name='Código de barra')
    up = models.IntegerField(default=0, verbose_name='Subida')
    down = models.IntegerField(default=0, verbose_name='Bajada')

    def __str__(self):
        return self.get_short_name()

    def get_full_name(self):
        return f'{self.name} ({self.code}) ({self.category.name}) = ${self.price}'

    def get_short_name(self):
        return f'{self.name} ({self.code}) | {self.up} - {self.down} = ${self.price}'

    def get_barcode(self):
        if self.barcode:
            return f'{settings.MEDIA_URL}{self.barcode}'
        return f'{settings.STATIC_URL}img/src/empty.png'

    def generate_barcode(self):
        image_io = BytesIO()
        Gs1_128(self.code, writer=writer.ImageWriter()).write(image_io)
        filename = f'{self.code}.png'
        self.barcode.save(filename, content=ContentFile(
            image_io.getvalue()), save=False)

    def as_dict(self):
        item = model_to_dict(self)
        item['value'] = self.get_full_name()
        item['full_name'] = self.get_full_name()
        item['short_name'] = self.get_short_name()
        item['category'] = self.category.as_dict()
        item['price'] = float(self.price)
        item['barcode'] = self.get_barcode()
        item['value'] = self.get_full_name()
        return item

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.generate_barcode()
        super(Product, self).save()

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['id']


class Receipt(models.Model):
    voucher_type = models.CharField(
        max_length=10, choices=VOUCHER_TYPE, verbose_name='Tipo de Comprobante')
    establishment_code = models.CharField(
        max_length=3, help_text='Ingrese un código de establecimiento emisor', verbose_name='Código del Establecimiento Emisor')
    issuing_point_code = models.CharField(
        max_length=3, help_text='Ingrese un código de punto de emisión', verbose_name='Código del Punto de Emisión')
    sequence = models.PositiveIntegerField(
        default=1, verbose_name='Secuencia actual')

    def __str__(self):
        return f'{self.name} - {self.establishment_code} - {self.issuing_point_code}'

    @property
    def name(self):
        return self.get_voucher_type_display()

    def get_name_file(self):
        return self.remove_accents(self.name.replace(' ', '_').lower()).upper()

    def remove_accents(self, text):
        return ''.join((c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'))

    def get_sequence(self):
        return f'{self.sequence:09d}'

    def as_dict(self):
        item = model_to_dict(self)
        item['name'] = self.name
        item['voucher_type'] = {'id': self.voucher_type,
                                'name': self.get_voucher_type_display()}
        return item

    class Meta:
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        ordering = ['id']


class ElecBillingDetailBase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0)
    tax = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0.00)
    price_with_tax = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)
    discount = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)
    total_discount = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=0.00)

    @property
    def tax_rate(self):
        return self.tax * 100

    def entity_to_dict(self):
        item = model_to_dict(self)
        item['product'] = self.product.as_dict()
        item['tax'] = float(self.tax)
        item['price'] = float(self.price)
        item['price_with_tax'] = float(self.price_with_tax)
        item['subtotal'] = float(self.subtotal)
        item['tax'] = float(self.tax)
        item['total_tax'] = float(self.total_tax)
        item['discount'] = float(self.discount)
        item['total_discount'] = float(self.total_discount)
        item['total_amount'] = float(self.total_amount)
        return item

    class Meta:
        abstract = True


class ReceiptErrors(models.Model):
    date_joined = models.DateField(
        default=datetime.now, verbose_name='Fecha de registro')
    time_joined = models.DateTimeField(
        default=datetime.now, verbose_name='Hora de registro')
    environment_type = models.PositiveIntegerField(
        choices=ENVIRONMENT_TYPE, default=ENVIRONMENT_TYPE[0][0], verbose_name='Tipo de entorno')
    receipt_number_full = models.CharField(
        max_length=50, verbose_name='Número de comprobante')
    receipt = models.ForeignKey(
        Receipt, on_delete=models.CASCADE, verbose_name='Tipo de Comprobante')
    stage = models.CharField(max_length=20, choices=VOUCHER_STAGE,
                             default=VOUCHER_STAGE[0][0], verbose_name='Etapa')
    errors = models.JSONField(default=dict, verbose_name='Errores')

    def __str__(self):
        return self.stage

    def as_dict(self):
        item = model_to_dict(self)
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['time_joined'] = self.time_joined.strftime('%Y-%m-%d %H:%M')
        item['environment_type'] = {
            'id': self.environment_type, 'name': self.get_environment_type_display()}
        item['receipt'] = self.receipt.as_dict()
        item['stage'] = {'id': self.stage, 'name': self.get_stage_display()}
        return item

    class Meta:
        verbose_name = 'Errores del Comprobante'
        verbose_name_plural = 'Errores de los Comprobantes'
        default_permissions = ()
        permissions = (
            ('view_receipt_errors', 'Can view Errores del Comprobante'),
            ('delete_receipt_errors', 'Can delete Errores del Comprobante'),
        )
        ordering = ['id']
