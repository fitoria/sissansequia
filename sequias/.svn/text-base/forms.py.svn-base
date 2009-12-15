 # -*- coding: UTF-8 -*-

from django import forms
from django.forms import ModelForm
from sequias.models import *
from lugar.models import *

date_inputformats=['%d.%m.%Y','%d/%m/%Y','%Y-%m-%d']

class SequiaForm(forms.Form):
    fecha_inicio = forms.DateField(input_formats=date_inputformats)
    fecha_final = forms.DateField(input_formats=date_inputformats)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, empty_label="Todos los Departamentos")
    municipio = forms.CharField(widget = forms.Select, required=False)
    comunidad = forms.CharField(widget = forms.Select, required=False)
    entrevistado = forms.CharField(widget = forms.Select, required=False)
    
