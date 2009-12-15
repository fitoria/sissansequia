from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from demografico.models import Poblacion
from lugar.models import Departamento
from django.db.models import Avg, Sum, Max, Min
from utils.pygooglechart import SimpleLineChart 
from django.utils import simplejson
from utils import grafos
#import datetime

#CHOICESANO=[]
#for i in range (datetime.date.today().year,1989,-1):
#	CHOICESANO.append((i,str(i)))

def __poblacion__(request, ano_inicial=None, ano_final=None, departamento=None):
    departamental=None
    departamentos = Departamento.objects.all()
    anos = Poblacion.objects.all().aggregate(ano_minimo = Min('ano'),
                                             ano_maximo = Max('ano'))
    try:
        rango_anos = range(int(anos['ano_minimo']), int(anos['ano_maximo'])+1)
    except:
        rango_anos = None

    if departamento:
        dept = get_object_or_404(Departamento, slug=departamento)
    else:
        dept=None
    if dept:
        if ano_inicial and ano_final:
            datos = Poblacion.objects.filter(ano__range=(ano_inicial, ano_final), departamento = dept)
            mensaje = "Poblacion del departamento de %s (%s-%s)" % (dept.nombre, ano_inicial, ano_final)
        elif ano_inicial:
            datos = Poblacion.objects.filter(ano=ano_inicial, departamento = dept)
            mensaje = "Poblacion del departamento de %s (%s)" % (dept.nombre, ano_inicial)
        else:
            datos = Poblacion.objects.filter(departamento = dept)
            mensaje = "Poblacion del departamento de %s" % (dept.nombre)
    else:
        datos = []
        if ano_inicial and ano_final:
            for ano in range(int(ano_inicial), int(ano_final)+1):
                resultado = Poblacion.objects.filter(ano=ano).aggregate(
                    hombre_urbano = Sum('hombre_urbano'),
                    mujer_urbano = Sum('mujer_urbano'),
                    hombre_rural = Sum('hombre_rural'),
                    mujer_rural = Sum('mujer_rural'),
                    total_hombre = Sum('total_hombre'),
                    total_mujer = Sum('total_mujer'))
                resultado['ano']=ano
                datos.append(resultado)
            mensaje = "Poblacion (%s-%s)" % (ano_inicial, ano_final)
        elif ano_inicial:
            resultado = Poblacion.objects.filter(ano=ano_inicial).aggregate(
                    hombre_urbano = Sum('hombre_urbano'),
                    mujer_urbano = Sum('mujer_urbano'),
                    hombre_rural = Sum('hombre_rural'),
                    mujer_rural = Sum('mujer_rural'),
                    total_hombre = Sum('total_hombre'),
                    total_mujer = Sum('total_mujer'))
            resultado['ano']=ano_inicial
            datos.append(resultado)
            mensaje = "Poblacion (%s)" % ano_inicial
        else:
            try:
                for ano in rango_anos:
                    resultado = Poblacion.objects.filter(ano=ano).aggregate(
                        hombre_urbano = Sum('hombre_urbano'),
                        mujer_urbano = Sum('mujer_urbano'),
                        hombre_rural = Sum('hombre_rural'),
                        mujer_rural = Sum('mujer_rural'),
                        total_hombre = Sum('total_hombre'),
                        total_mujer = Sum('total_mujer'))
                    resultado['ano']=ano
                    datos.append(resultado)
            except TypeError:
                pass
            mensaje = "Poblacion total"

    totales = {'hombre_urbano': 0, 'hombre_rural': 0,
               'mujer_urbano': 0, 'mujer_rural': 0,
               'total_hombre': 0, 'total_mujer': 0}

    for cosito in datos:
        if type(cosito)==dict:
            departamental=False
            totales['hombre_urbano'] += cosito['hombre_urbano'] if cosito['hombre_urbano'] != None else 0
            totales['hombre_rural'] += cosito['hombre_rural'] if cosito['hombre_urbano'] != None else 0
            totales['mujer_urbano'] += cosito['mujer_urbano'] if cosito['hombre_urbano'] != None else 0
            totales['mujer_rural'] += cosito['mujer_rural'] if cosito['hombre_urbano'] != None else 0
            totales['total_hombre'] += cosito['total_hombre'] if cosito['hombre_urbano'] != None else 0
            totales['total_mujer'] += cosito['total_mujer'] if cosito['hombre_urbano'] != None else 0
        else:
            departamental=True
            totales['hombre_urbano'] += cosito.hombre_urbano 
            totales['hombre_rural'] += cosito.hombre_rural
            totales['mujer_urbano'] += cosito.mujer_urbano
            totales['mujer_rural'] += cosito.mujer_rural
            totales['total_hombre'] += cosito.total_hombre
            totales['total_mujer'] += cosito.total_mujer

    dicc = {'totales': totales, 'datos': datos, 'mensaje': mensaje, 
            'departamental': departamental, 'anos': rango_anos, 'departamentos': departamentos}
    return dicc 

def poblacion(request, ano_inicial=None, ano_final=None, departamento=None):
    dicc = __poblacion__(request, ano_inicial, ano_final, departamento)
    return render_to_response('demografico/poblacion.html', dicc)

def grafo_poblacion(request, ano_inicial=None, ano_final=None, departamento=None):
    datos = __poblacion__(request, ano_inicial, ano_final, departamento)
    if not datos['departamental']:
        hombre_urbano = [foo['hombre_urbano'] for foo in datos['datos']]
        mujer_urbano = [foo['mujer_urbano'] for foo in datos['datos']]
        mujer_rural = [foo['mujer_rural'] for foo in datos['datos']]
        hombre_rural = [foo['hombre_rural'] for foo in datos['datos']]
        
    else:
        hombre_urbano = [foo.hombre_urbano for foo in datos['datos']]
        mujer_urbano = [foo.mujer_urbano for foo in datos['datos']]
        hombre_rural = [foo.hombre_rural for foo in datos['datos']]
        mujer_rural = [foo.mujer_rural for foo in datos['datos']]

    numeros = [hombre_urbano, mujer_urbano, hombre_rural, mujer_rural]
    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis=ano_inicial
    else:
        axis = datos['anos']
    leyendas = ['Hombre Urbano', 'Mujer Urbana', 'Hombre Rural', 'Mujer Rural']
    
    return grafos.make_graph(numeros, leyendas, datos['mensaje'],
                             axis, type=SimpleLineChart, multiline=True, steps=6, size=(600,500))
