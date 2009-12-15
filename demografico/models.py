# -*- coding: UTF-8 -*-
from django.db import models
from lugar.models import Departamento
import datetime

CHOICESANO=[]
for i in range (datetime.date.today().year,1989,-1):
    CHOICESANO.append((i,str(i)))

class Poblacion(models.Model):
    ano = models.IntegerField("Año",max_length=5, choices=CHOICESANO, help_text='Introduzca el año')
    departamento = models.ForeignKey(Departamento,help_text='Introduzca nombre del departamento')
    total_ambos_sexos = models.IntegerField("Total de ambos sexos",max_length=10, editable=False)
    total_hombre = models.IntegerField("Total hombres",max_length=10, editable=False)
    total_mujer = models.IntegerField("Total mujer",max_length=10, editable=False)
    total_urbano = models.IntegerField("Ambos sexos urbano",max_length=10, editable=False)
    hombre_urbano = models.IntegerField("Hombre urbano",max_length=10)
    mujer_urbano = models.IntegerField("Mujer urbano",max_length=10)
    total_rural = models.IntegerField("Ambos sexos rural",max_length=10, editable=False)
    hombre_rural = models.IntegerField("Hombre rural",max_length=10)
    mujer_rural = models.IntegerField("Mujer rural",max_length=10)

    class Meta:
        ordering = ['ano']
        verbose_name_plural = "Indicador de Poblacion"
        unique_together = ['ano','departamento']

    def save(self, force_insert=False, force_update=False):
        self.total_rural = self.hombre_rural + self.mujer_rural
        self.total_urbano = self.hombre_urbano + self.mujer_urbano
        self.total_hombre = self.hombre_rural + self.hombre_urbano
        self.total_mujer = self.mujer_rural + self.mujer_urbano
        self.total_ambos_sexos = self.total_hombre + self.total_mujer
        super(Poblacion,self).save(force_insert, force_update)

    def __unicode__(self):
        return"Poblacion %s - %s" % (self.departamento.nombre, self.ano)

    def densidad(self):
        return "%.2f" % (self.total_ambos_sexos/self.departamento.extension)
