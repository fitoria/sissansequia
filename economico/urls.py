from django.conf.urls.defaults import *
from django.conf import settings
 
urlpatterns = patterns('economico.views',
                        (r'^$', 'index'),
                        (r'^economico/canasta-basica/$', 'canasta_basica'),
                        (r'^economico/canasta-basica/tipo/(?P<tipo>[\w-]+)/$', 'canasta_basica'),
                        (r'^economico/canasta-basica/(?P<ano_inicial>\d{4})/$', 'canasta_basica'),
                        (r'^economico/canasta-basica/(?P<ano_inicial>\d{4})/tipo/(?P<tipo>[\w-]+)/$', 'canasta_basica'),
                        (r'^economico/canasta-basica/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'canasta_basica'),
                        (r'^economico/canasta-basica/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/tipo/(?P<tipo>\w+)/$', 'canasta_basica'),
                        #grafo canasta basica
                        (r'^economico/grafo/canasta-basica/$', 'grafo_canasta_basica'),
                        (r'^economico/grafo/canasta-basica/tipo/(?P<tipo>[\w-]+)/$', 'grafo_canasta_basica'),
                        (r'^economico/grafo/canasta-basica/(?P<ano_inicial>\d{4})/$', 'grafo_canasta_basica'),
                        (r'^economico/grafo/canasta-basica/(?P<ano_inicial>\d{4})/tipo/(?P<tipo>[\w-]+)/$', 'grafo_canasta_basica'),
                        (r'^economico/grafo/canasta-basica/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_canasta_basica'),
                        (r'^economico/grafo/canasta-basica/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/tipo/(?P<tipo>\w+)/$', 'grafo_canasta_basica'),
                        #mercados
                        (r'^economico/mercados/$', 'mercados'),
                        (r'^economico/mercados/departamento/(?P<departamento>\d+)/$', 'mercados'),
                        (r'^economico/mercados/municipio/(?P<municipio>\d+)/$', 'mercados'),
                        #empleo
                        (r'^economico/empleo/$', 'empleo'),
                        (r'^economico/empleo/(?P<ano_inicial>\d{4})/$', 'empleo'),
                        (r'^economico/empleo/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'empleo'),
                        #salario minimo
                        (r'^economico/salario-minimo/$', 'salario_minimo'),
                        (r'^economico/salario-minimo/sector/(?P<sector>[\w-]+)/$', 'salario_minimo'),
                        (r'^economico/salario-minimo/(?P<ano_inicial>\d{4})/$', 'salario_minimo'),
                        (r'^economico/salario-minimo/(?P<ano_inicial>\d{4})/sector/(?P<sector>[\w-]+)/$', 'salario_minimo'),
                        (r'^economico/salario-minimo/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'salario_minimo'),
                        (r'^economico/salario-minimo/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/sector/(?P<sector>\w+)/$', 'salario_minimo'),
                        #grafo salario minimo
                        (r'^economico/grafo/salario-minimo/$', 'grafo_salario_minimo'),
                        (r'^economico/grafo/salario-minimo/sector/(?P<sector>[\w-]+)/$', 'grafo_salario_minimo'),
                        (r'^economico/grafo/salario-minimo/(?P<ano_inicial>\d{4})/$', 'grafo_salario_minimo'),
                        (r'^economico/grafo/salario-minimo/(?P<ano_inicial>\d{4})/sector/(?P<sector>[\w-]+)/$', 'grafo_salario_minimo'),
                        (r'^economico/grafo/salario-minimo/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_salario_minimo'),
                        (r'^economico/grafo/salario-minimo/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/sector/(?P<sector>\w+)/$', 'grafo_salario_minimo'),
                        #salario nominal real
                        (r'^economico/salario-nominal-real/$', 'salario_nominal_real'),
                        (r'^economico/salario-nominal-real/(?P<ano_inicial>\d{4})/$', 'salario_nominal_real'),
                        (r'^economico/salario-nominal-real/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'salario_nominal_real'),
                        #grafo salario nominal real
                        (r'^economico/grafo/salario-nominal-real/$', 'grafo_salario_nominal_real'),
                        (r'^economico/grafo/salario-nominal-real/(?P<ano_inicial>\d{4})/$', 'grafo_salario_nominal_real'),
                        (r'^economico/grafo/salario-nominal-real/(?P<ano_inicial>\d{4})-(?P<ano_final>\d{4})/$', 'grafo_salario_nominal_real'),
                       )
