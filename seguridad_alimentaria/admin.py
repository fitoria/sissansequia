from django.contrib import admin
from seguridad_alimentaria.models import *

class ProductoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
class SoberaniaAlimentariaAdmin(admin.ModelAdmin):
    list_filter = ['ano', 'producto']
class UtilizacionBiologicaAdmin(admin.ModelAdmin):
    list_filter = ['ano', 'departamento']
class DependenciaAlimentariaAdmin(admin.ModelAdmin):
    list_filter = ['producto', 'ano']
class AperturaComercialAdmin(admin.ModelAdmin):
    pass

admin.site.register(Producto, ProductoAdmin)
admin.site.register(DependenciaAlimentaria, DependenciaAlimentariaAdmin)
admin.site.register(SoberaniaAlimentaria, SoberaniaAlimentariaAdmin)
admin.site.register(UtilizacionBiologica, UtilizacionBiologicaAdmin)
admin.site.register(AperturaComercial, AperturaComercialAdmin)
