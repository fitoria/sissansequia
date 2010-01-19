from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('demografico.views',
     #grafos poblacion
    (r'^grafo/poblacion/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    (r'^grafo/poblacion/(?P<departamento>[\w-]+)/$', 'grafo_poblacion'),
    #grafo densidad
    (r'^grafo/densidad/$', 'grafo_densidad'),
    (r'^grafo/densidad/(?P<ano_inicial>\d{4})/$', 'grafo_densidad'),
    (r'^grafo/densidad/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_densidad'),
    (r'^grafo/densidad/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_densidad'),
    (r'^grafo/densidad/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'grafo_densidad'),
    (r'^grafo/densidad/(?P<departamento>[\w-]+)/$', 'grafo_densidad'),
    #poblacion
    (r'^poblacion/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'poblacion'),
    (r'^poblacion/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'poblacion'),
    (r'^poblacion/(?P<departamento>[\w-]+)/$', 'poblacion'),
    #densidad
    (r'^densidad/$', 'densidad'),
    (r'^densidad/(?P<ano_inicial>\d{4})/$', 'densidad'),
    (r'^densidad/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'densidad'),
    (r'^densidad/(?P<ano_inicial>\d{4})/(?P<departamento>[\w-]+)/$', 'densidad'),
    (r'^densidad/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/(?P<departamento>[\w-]+)/$', 'densidad'),
    (r'^densidad/(?P<departamento>[\w-]+)/$', 'densidad'),
)
