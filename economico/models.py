# -*- coding: UTF-8 -*-
from django.db import models
import datetime
from lugar.models import Departamento, Municipio

ANO_CHOICES=[]
for i in range (datetime.date.today().year,1989,-1):
	ANO_CHOICES.append((i,str(i)))

MES_CHOICES = (
    (1, 'Enero'),(2, 'Febrero'),(3, 'Marzo'),(4, 'Abril'),(5, 'Mayo'),(6, 'Junio'),(7, 'Julio'),(8, 'Agosto'),(9, 'Septiembre'), (10, 'Octubre'),(11, 'Noviembre'),(12, 'Diciembre')
)

#class Exportacion(models.Model):
#	ano = models.IntegerField("Ano",max_length=5, choices=CHOICESANO, help_text='Introduzca el ano')
#	mes = models.IntegerField("Mes",max_length=2, choices=CHOICESMES, help_text='Introduzca el mes')
#	fob = models.DecimalField("FOB",max_digits=10,decimal_places=2)
#
#	class Meta:
#		ordering = ['ano']
#		unique_together = ['ano','mes']
#		verbose_name_plural = "Indicador de Exportaciones de Mercancias FOB"

	#def __unicode__(self):
	#	return self.ano

class Sector(models.Model):
    nombre = models.CharField("Nombre del Sector", max_length=50, unique=True)
    slug = models.SlugField(unique=True, null=True)

    def __unicode__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural='Sectores'

class SalarioMinimo(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    mes = models.IntegerField("Mes", max_length=2, choices=MES_CHOICES)
    sector = models.ForeignKey(Sector)
    salario = models.DecimalField("Salario", max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "Salario Minimo sector %s (%s-%s)" % (self.sector.nombre, self.mes, self.ano)

    class Meta:
        unique_together=['ano','mes','sector']
        ordering = ['ano']
        verbose_name_plural = "indicador de salario minimo"
        verbose_name = verbose_name_plural

class TipoCanastaBasica(models.Model):
    tipo = models.CharField("Tipo", unique=True, max_length=30)
    slug = models.SlugField("slug", unique=True, max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.tipo

    class Meta:
        verbose_name_plural='Tipos de Canastas Basicas'

class CanastaBasica(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    tipo = models.ForeignKey(TipoCanastaBasica, null=True, blank=True)
    mes = models.IntegerField("Mes", max_length=2, choices=MES_CHOICES)
    costo = models.DecimalField("Costo", max_digits=14, decimal_places=2)

    def __unicode__(self):
        return "Canasta Basica %s-%s" % (self.mes, self.ano)

    class Meta:
        ordering = ['tipo', 'ano', 'mes']
        unique_together=['tipo','mes', 'ano']

class SalarioNominal(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    mes = models.IntegerField("Mes", max_length=2, choices=MES_CHOICES)
    asegurados_inss = models.DecimalField("Asegurados del INSS", max_digits=10, decimal_places=2)
    gobierno_central = models.DecimalField("Gobierno Central", max_digits=10, decimal_places=2)
    salario_nacional = models.DecimalField("Salario nacional", max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "Salario Nominal %s-%s" % (self.mes, self.ano)

    class Meta:
        unique_together=['ano','mes']
        ordering = ['ano', 'mes']
        verbose_name_plural = "indicador de salario nominal"
        verbose_name = verbose_name_plural

class SalarioReal(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    mes = models.IntegerField("Mes", max_length=2, choices=MES_CHOICES)
    asegurados_inss = models.DecimalField("Asegurados del INSS", max_digits=10, decimal_places=2)
    gobierno_central = models.DecimalField("Gobierno Central", max_digits=10, decimal_places=2)
    salario_nacional = models.DecimalField("Salario nacional", max_digits=10, decimal_places=2)

    def __unicode__(self):
        return "Salario Real %s-%s" % (self.mes, self.ano)

    class Meta:
        unique_together=['ano', 'mes']
        ordering = ['ano', 'mes']
        verbose_name_plural = "indicador de salario Real"
        verbose_name = verbose_name_plural

class Mercado(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    departamento = models.ForeignKey(Departamento)
    municipio = models.ForeignKey(Municipio)
    nombre = models.CharField("Nombre", max_length=100)
    ubicacion = models.TextField("Ubicacion")

    def __unicode__(self):
        return "Mercado: %s en %s, %s" % (self.nombre, self.municipio.nombre, self.departamento.nombre)

    class Meta:
        unique_together = ['ano', 'nombre']
        ordering = ['nombre']

class FuerzaTrabajo(models.Model):
    ano = models.IntegerField("Año", max_length=4, choices=ANO_CHOICES)
    poblacion_total = models.IntegerField()
    poblacion_mayor_10 = models.IntegerField()
    pea_general = models.IntegerField()
    total_ocupados = models.IntegerField()
    ocupados_actividad_primaria = models.IntegerField()
    agricultura_pecuaria = models.IntegerField()
    silvicultura = models.IntegerField()
    pesca = models.IntegerField()
    ocupados_actividad_secundaria = models.IntegerField()
    manufactura = models.IntegerField("Industria Manufacturera")
    construccion = models.IntegerField("Construccion")
    minas_canteras = models.IntegerField("Minas y Canteras")
    ocupados_actividad_terciaria = models.IntegerField("Ocupados Actividad Terciaria")
    comercio = models.IntegerField()
    gobierno_central = models.IntegerField()
    transporte_comunicacion = models.IntegerField("Transporte y Comunicacion")
    establecimientos_financieros = models.IntegerField("Establecimientos Financieros")
    electricidad_gas_agua = models.IntegerField("Electricidad Gas y Agua") 
    desempleo_abierto = models.IntegerField("Desempleo Abierto", editable=False) #se calcula
    servicios_sociales = models.DecimalField("Serv. Soc. Comun. y Personales", max_digits=10, decimal_places=2, default = 0) 

    def __unicode__(self):
        return "Fuerza de Trabajo: %s" %  self.ano

    def save(self, force_insert=False, force_update=False):
        self.desempleo_abierto = self.pea_general - self.total_ocupados 
        super(FuerzaTrabajo, self).save(force_insert, force_update)

    class Meta:
        ordering = ['ano']
        verbose_name = 'Fuerza de Trabajo'
        verbose_name_plural = verbose_name
