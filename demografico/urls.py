from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('demografico.views',
     #grafos
    (r'^grafo/poblacion/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    #normalitas
    (r'^poblacion/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'poblacion'),
    (r'^poblacion/(?P<departamento>[\w-]+)/$', 'poblacion'),
)
