from django.db import models
import datetime
from lugar.models import Departamento

ANO_CHOICES=[]
for i in range (datetime.date.today().year,1989,-1):
	ANO_CHOICES.append((i,str(i)))
#disp y consumo aparente

class Producto(models.Model):
    nombre = models.CharField("Nombre del Producto", max_length=20)
    slug = models.SlugField("url limpia", null=True)

    def __unicode__(self):
        return self.nombre

class DependenciaAlimentaria(models.Model):
    ano = models.IntegerField("Ano", max_length=4, choices=ANO_CHOICES)
    producto = models.ForeignKey(Producto)
    area = models.DecimalField(help_text = "miles de manzanas", max_digits=10, decimal_places=2)
    produccion = models.DecimalField(max_digits=10, decimal_places=2, help_text="en miles de quintales")
    rendimiento= models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    donaciones = models.DecimalField(max_digits=10, decimal_places=2, help_text="en miles de quintales")
    exportaciones = models.DecimalField(max_digits=10, decimal_places=2, help_text="en miles de quintales")
    importaciones = models.DecimalField(max_digits=10, decimal_places=2, help_text="en miles de quintales")
    dependencia_alimentaria = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    porcentaje = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, force_insert=False, force_update=False):
        self.rendimiento = self.produccion/self.area
        self.dependencia_alimentaria = self.produccion + self.importaciones + self.donaciones - self.exportaciones
        self.porcentaje = ((self.importaciones + self.donaciones)/self.dependencia_alimentaria)*100 
        super(DependenciaAlimentaria, self).save(force_insert, force_update)

    def __unicode__(self):
        return "Dependencia alimentaria - %s (%s)" % (self.producto.nombre, self.ano)
    
    class Meta:
        unique_together=['ano', 'producto']
        ordering = ['ano', 'producto']
        verbose_name_plural = 'Dependencia Alimentaria'


class SoberaniaAlimentaria(models.Model):
    ano = models.IntegerField("Ano", max_length=4, choices=ANO_CHOICES)
    producto = models.ForeignKey(Producto)
    donaciones = models.DecimalField(max_digits=10, decimal_places=2)
    importaciones = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidad = models.DecimalField(max_digits=10, decimal_places=2)
    consumo_aparente= models.DecimalField(max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "%s (%s)" % (self.producto.nombre, self.ano)

    class Meta:
        unique_together=['ano','producto']
        ordering=['ano', 'producto']
        verbose_name = "Soberania Alimentaria"
        verbose_name_plural = verbose_name

class UtilizacionBiologica(models.Model):
    ano = models.IntegerField("Ano", max_length=4, choices=ANO_CHOICES)
    departamento = models.ForeignKey(Departamento)
    enfermedades_diarreicas = models.DecimalField("Enfermedades diarreicas agudas", max_digits=10, decimal_places=2)
    enfermedades_respiratorias = models.DecimalField("Enfermedades respiratorias agudas", max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "Utilizacion bioligica dept: %s (%s)" % (self.departamento.nombre, self.ano)

    class Meta:
        unique_together=['ano','departamento']
        ordering=['-ano']
        verbose_name = "Utilizacion Biologica"
        verbose_name_plural = verbose_name

class AperturaComercial(models.Model):
    ano = models.IntegerField("Ano", max_length=4, choices=ANO_CHOICES, unique=True)
    pib = models.DecimalField("PIB", decimal_places=2, max_digits=10)
    exportaciones = models.DecimalField("Exportaciones", decimal_places=2, max_digits=10)
    importaciones = models.DecimalField("Importaciones", decimal_places=2, max_digits=10)

    def __unicode__(self):
        return "Apertura Comercial (%s)" % self.ano

    class Meta:
        ordering=['-ano']
        verbose_name = "Apertura Comercial"
        verbose_name_plural = "Aperturas Comerciales"
