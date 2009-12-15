from django import forms
import datetime

ANO_CHOICES=[]
for i in range (datetime.date.today().year,1989,-1):
    ANO_CHOICES.append((i, str(i)))

class AnoFilterForm(form.Forms):
   ano_inicial = form.ChoiceField(choides=ANO_CHOICES) 
   ano_final = form.ChoiceField(choides=ANO_CHOICES, empty_label="Ninguno") 
