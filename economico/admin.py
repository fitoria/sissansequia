from django.contrib import admin
from economico.models import *

class MercadoAdmin(admin.ModelAdmin):
    list_filter = ['departamento']
class SectorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}
class CanastaBasicaAdmin(admin.ModelAdmin):
    list_filter = ['ano', 'tipo']
class SalarioNominalAdmin(admin.ModelAdmin):
    list_filter = ['ano']
class SalarioRealAdmin(admin.ModelAdmin):
    list_filter = ['ano']
class SalarioMinimoAdmin(admin.ModelAdmin):
    list_filter = ['ano']
class FuerzaTrabajoAdmin(admin.ModelAdmin):
    list_filter = ['ano']
class TipoCanastaBasicaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("tipo",)}


admin.site.register(Mercado, MercadoAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(CanastaBasica, CanastaBasicaAdmin)
admin.site.register(SalarioNominal, SalarioNominalAdmin)
admin.site.register(SalarioMinimo, SalarioMinimoAdmin)
admin.site.register(SalarioReal, SalarioRealAdmin)
admin.site.register(FuerzaTrabajo, FuerzaTrabajoAdmin)
admin.site.register(TipoCanastaBasica, TipoCanastaBasicaAdmin)
