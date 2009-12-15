from django.contrib import admin
from demografico.models import Poblacion

class PoblacionAdmin(admin.ModelAdmin):
	list_filter = ['ano']
	#search_fields = ['departamento']

admin.site.register(Poblacion, PoblacionAdmin)



