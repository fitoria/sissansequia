from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse
from django.db.models import Sum, Max, Min
from demografico.models import Poblacion
from utils import grafos
from utils.pygooglechart import SimpleLineChart
from models import *

def index(request):
    pass

def dependencia_alimentaria(request, ano_inicial=None, ano_final=None):
    dicc = __dependencia_alimentaria__(request, ano_inicial, ano_final)
    return render_to_response("seguridad_alimentaria/dependencia_alimentaria.html", dicc)

def grafo_dependencia_alimentaria(request, ano_inicial=None, ano_final=None):
    dicc = __dependencia_alimentaria__(request, ano_inicial, ano_final)
    rows_2_column = []
    
    for producto in dicc['productos']:
        rows_2_column.append([])

    for row in dicc['resultados']:
        for i in range(len(row['datos'])):
            rows_2_column[i].append(float(row['datos'][i]))

    data = [row for row in rows_2_column]
    legends = [producto.nombre for producto in dicc['productos']]
    message = "Dependencia Alimentaria"

    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis = ano_inicial
    else:
        axis = dicc['anos']

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart, multiline=True)

def __dependencia_alimentaria__(request, ano_inicial=None, ano_final=None):
    productos = Producto.objects.all()
    resultados = []
    try:
        limites = DependenciaAlimentaria.objects.all().aggregate(maximo=Max('ano'), minimo=Min('ano'))
        rango_anos = range(limites['minimo'], limites['maximo']+1)
    except:
        rango_anos = None

    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            fila = {'ano': ano, 'datos': []}
            for producto in productos:
                try:
                    dato = DependenciaAlimentaria.objects.get(ano=ano, producto = producto)
                    fila['datos'].append(dato.dependencia_alimentaria)
                except: 
                    fila['datos'].append(0)

            resultados.append(fila)
    elif ano_inicial:
        fila = {'ano': ano_inicial, 'datos':[]}
        for producto in productos:
            try:
                dato = DependenciaAlimentaria.objects.get(ano=ano_inicial, producto= producto)
                fila['datos'].append(dato.dependencia_alimentaria)
            except:
                fila['datos'].append(0)
        resultados.append(fila)
    else:
        try:
            for ano in rango_anos: 
                fila = {'ano': ano, 'datos': []}
                for producto in productos:
                    try:
                        dato = DependenciaAlimentaria.objects.get(ano=ano, producto=producto)
                        fila['datos'].append(dato.dependencia_alimentaria)
                    except:
                        fila['datos'].append(0)
                resultados.append(fila) 
        except:
            pass

    variaciones = []
    try:
        tope = len(resultados) - 1 
        fila_inicial = resultados[0]['datos']
        fila_final = resultados[tope]['datos']
    except:
        tope = 0
        fila_inicial = None
        fila_final = None
    for i in range(tope):
        try:
            variacion = ((fila_final[i]-fila_inicial[i])/fila_inicial[i])*100 if fila_inicial[i]!=0 else 100 
        except:
            variacion = 0
        variaciones.append("%.2f" % variacion) 

    dicc = {'resultados': resultados, 'variaciones': variaciones, 
            'productos': productos, 'anos': rango_anos, 'productos_all': productos}
    return dicc

def dependencia_alimentaria_producto(request, producto, ano_inicial=None, ano_final=None):
    dicc = __dependencia_alimentaria_producto__(request, producto, ano_inicial, ano_final)
    return render_to_response("seguridad_alimentaria/dependencia_alimentaria.html", dicc)

def grafo_dependencia_alimentaria_producto(request, producto, ano_inicial=None, ano_final=None):
    dicc = __dependencia_alimentaria_producto__(request, producto, ano_inicial, ano_final)
    rows_2_column = []
    
    for producto in dicc['productos']:
        rows_2_column.append([])

    for row in dicc['resultados']:
        for i in range(len(row['datos'])):
            rows_2_column[i].append(float(row['datos'][i]))

    data = [row for row in rows_2_column]
    legends = [producto.nombre for producto in dicc['productos']]
    message = "Dependencia Alimentaria"

    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis = ano_inicial
    else:
        axis = dicc['anos']

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart, multiline=True)

def __dependencia_alimentaria_producto__(request, producto, ano_inicial=None, ano_final=None):
    producto = get_object_or_404(Producto, slug=producto)
    productos = [producto]
    try:
        limites = DependenciaAlimentaria.objects.all().aggregate(maximo=Max('ano'), minimo=Min('ano'))
        rango_anos = range(limites['minimo'], limites['maximo']+1)
    except: 
        rango_anos = None

    resultados = []
    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            fila = {'ano': ano, 'datos': []}
            try:
                dato = DependenciaAlimentaria.objects.get(ano=ano, producto = producto)
                fila['datos'].append(dato.dependencia_alimentaria)
            except:
                fila['datos'].append(0)
            resultados.append(fila)
    elif ano_inicial:
        fila = {'ano': ano_inicial, 'datos':[]}
        try:
            dato = DependenciaAlimentaria.objects.get(ano=ano_inicial, producto= producto)
            fila['datos'].append(dato.dependencia_alimentaria)
        except:
            fila['datos'].append(0)
        resultados.append(fila)
    else:
        try:
            for ano in rango_anos:
                fila = {'ano': ano, 'datos': []}
                try:
                    dato = DependenciaAlimentaria.objects.get(ano=ano, producto=producto)
                    fila['datos'].append(dato.dependencia_alimentaria)
                except:
                    fila['datos'].append(0)
                resultados.append(fila) 
        except: 
            pass

    variaciones = []
    tope = len(resultados) - 1 
    try:
        fila_inicial = resultados[0]['datos']
        fila_final = resultados[tope]['datos']
        variacion = ((fila_final[0]-fila_inicial[0])/fila_inicial[0])*100 if fila_inicial[0]!=0 else 0
        variaciones.append("%.2f" % variacion) 
    except:
        pass


    dicc = {'resultados': resultados, 'variaciones': variaciones, 'anos': rango_anos, 
            'productos': productos, 'productos_all': Producto.objects.all()}
    return dicc

def utilizacion_biologica(request, ano_inicial=None, ano_final=None, departamento=None):
    dicc = __utilizacion_biologica__(request, ano_inicial, ano_final, departamento)
    return render_to_response('seguridad_alimentaria/utilizacion_biologica.html', dicc)

def grafo_utilizacion_biologica(request, ano_inicial=None, ano_final=None, departamento=None):
    dicc = __utilizacion_biologica__(request, ano_inicial, ano_final, departamento)
    if not dicc['departamento']:
        enfermedades_diarreicas = [float(foo['enfermedades_diarreicas']) for foo in dicc['datos']]
        enfermedades_respiratorias= [float(foo['enfermedades_respiratorias']) for foo in dicc['datos']]
    else:
        enfermedades_diarreicas = [float(foo.enfermedades_diarreicas) for foo in dicc['datos']]
        enfermedades_respiratorias= [float(foo.enfermedades_respiratorias) for foo in dicc['datos']]

    data = [enfermedades_diarreicas, enfermedades_respiratorias]
    legends = ['Enfermedades Diarreicas', 'Enfermedades Respiratorias']

    message = 'Utilizacion Biologica'

    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis=ano_inicial
    else:
        axis = dicc['anos']

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart, multiline=True)

def __utilizacion_biologica__(request, ano_inicial=None, ano_final=None, departamento=None):
    departamentos = Departamento.objects.all()
    try:
        anos = UtilizacionBiologica.objects.all().aggregate(ano_minimo = Min('ano'), ano_maximo= Max('ano'))
        rango_anos = range(anos['ano_minimo'], anos['ano_maximo']+1) 
    except:
        rango_anos = None

    if departamento:
        tiene_dep=True
        nombre_dep = get_object_or_404(Departamento, slug=departamento).nombre
        if ano_inicial and ano_final:
            datos = UtilizacionBiologica.objects.filter(ano__range=(ano_inicial, ano_final), departamento__slug =departamento)
            mensaje = "Utilizacion Biologica departamento de %s (%s-%s)" % (nombre_dep, ano_inicial, ano_final)
        elif ano_inicial:
            datos = UtilizacionBiologica.objects.filter(ano=ano_inicial, departamento__slug =departamento)
            mensaje = "Utilizacion Biologica departamento %s (%s)" % (nombre_dep, ano_inicial)
        else:
            datos = UtilizacionBiologica.objects.filter(departamento__slug = departamento)
            mensaje = "Utilizacion Biologica departamento %s" % nombre_dep
        indice = len(datos) - 1
        variacion_eda = ((datos[indice].enfermedades_diarreicas - datos[0].enfermedades_diarreicas)/(datos[0].enfermedades_diarreicas)) * 100
        variacion_ira = ((datos[indice].enfermedades_respiratorias - datos[0].enfermedades_respiratorias)/(datos[0].enfermedades_diarreicas)) * 100
    else:
        datos = []
        tiene_dep=False
        if ano_inicial and ano_final:
            for ano in range(int(ano_inicial), int(ano_final)+1):
                resultado = UtilizacionBiologica.objects.filter(ano=ano).aggregate(
                    enfermedades_diarreicas=Sum('enfermedades_diarreicas'), 
                    enfermedades_respiratorias=Sum('enfermedades_respiratorias'))
                resultado['ano']=ano
                datos.append(resultado)
            mensaje = "Utilizacion Biologica (%s-%s)" % (ano_inicial, ano_final)
        elif ano_inicial:
            resultado = UtilizacionBiologica.objects.filter(ano=ano_inicial).aggregate(
                enfermedades_diarreicas=Sum('enfermedades_diarreicas'), 
                enfermedades_respiratorias=Sum('enfermedades_respiratorias'))
            resultado['ano']=ano_inicial
            datos.append(resultado)
            mensaje = "Utilizacion Biologica (%s)" % (ano_inicial)
        else:
            try:
                for ano in rango_anos:
                    resultado = UtilizacionBiologica.objects.filter(ano=ano).aggregate(
                        enfermedades_diarreicas=Sum('enfermedades_diarreicas'), 
                        enfermedades_respiratorias=Sum('enfermedades_respiratorias'))
                    resultado['ano']=ano
                    datos.append(resultado)
                mensaje = "Utilizacion Biologica" 
            except TypeError:
                mensaje = "error" 

        datos.reverse()
        indice = len(datos)-1
        try:
            variacion_eda = ((datos[indice]['enfermedades_diarreicas']-datos[0]['enfermedades_diarreicas'])/(datos[0]['enfermedades_diarreicas']))*100
            variacion_ira = ((datos[indice]['enfermedades_respiratorias']-datos[0]['enfermedades_respiratorias'])/(datos[0]['enfermedades_respiratorias']))*100 
        except :
            variacion_eda = 0 
            variacion_ira = 0
    variaciones = {'variacion_eda': variacion_eda, 'variacion_ira': variacion_ira}
    dicc = {'datos': datos, 'mensaje': mensaje, 'variaciones': variaciones, 'departamento': tiene_dep,
            'departamentos':departamentos , 'anos':rango_anos }
    return dicc


def disponibilidad(request, ano_inicial=None, ano_final=None, producto=None):
    dicc = __disponibilidad__(request, ano_inicial, ano_final, producto)
    return render_to_response('seguridad_alimentaria/disponibilidad.html', dicc)

def grafo_disponibilidad(request, ano_inicial=None, ano_final=None, producto=None):
    dicc = __disponibilidad__(request, ano_inicial, ano_final, producto)

    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis = ano_inicial
    else:
        axis = dicc['anos']

    rows_2_column = []
    #Para los consumos
    for producto in dicc['productos']:
        rows_2_column.append([])

    for row in dicc['consumos']:
        for i in range(len(row['datos'])):
            rows_2_column[i].append(float(row['datos'][i]))

    data = [row for row in rows_2_column]
    legends = [producto.nombre for producto in dicc['productos']]
    message = "Dependencia Alimentaria"
    url_grafo_consumos = grafos.make_graph(data, legends, message, axis, 
                                           type=SimpleLineChart, multiline=True, return_json=False)

    ##Para las disponibilidades
    rows_2_column = []
    for producto in dicc['productos']:
        rows_2_column.append([])

    for row in dicc['disponibilidades']:
        for i in range(len(row['datos'])):
            rows_2_column[i].append(float(row['datos'][i]))

    data = [row for row in rows_2_column]
    legends = [producto.nombre for producto in dicc['productos']]
    message = "Dependencia Alimentaria"
    url_grafo_disponibilidades = grafos.make_graph(data, legends, message, axis, 
                                                   type=SimpleLineChart, multiline=True, return_json=False)

    json_dicc = {'url_consumos': url_grafo_consumos, 'url_disponibilidades': url_grafo_disponibilidades}

    return HttpResponse(simplejson.dumps(json_dicc), mimetype="application/javascript")

def __disponibilidad__(request, ano_inicial=None, ano_final=None, producto=None):
    #formula disp = produccion + importaciones + donaciones + exportaciones (dependencia alimentaria)
    #consumo aparente = disp/poblacion
    disponibilidades = []
    consumos = []
    columnas = []
    productos_all = Producto.objects.all()
    try:
        anos = DependenciaAlimentaria.objects.all().aggregate(minimo = Min('ano'), maximo= Max('ano'))
        rango_anos = range(anos['minimo'], anos['maximo']+1)
    except:
        rango_anos = None
    if producto:
        producto = get_object_or_404(Producto, slug=producto)
        productos = [producto]
    else:
        productos = productos_all 
    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            poblacion = Poblacion.objects.filter(ano=ano).aggregate(total=Sum('total_ambos_sexos'))
            fila_disp = {'ano': ano, 'datos': []}
            fila_consumo = {'ano': ano, 'datos': []}
            for producto in productos:
                dependencia = DependenciaAlimentaria.objects.get(ano=ano, producto=producto)
                disponibilidad = dependencia.produccion + dependencia.importaciones + dependencia.donaciones - dependencia.exportaciones
                consumo_aparente = disponibilidad/poblacion['total']
                fila_disp['datos'].append(disponibilidad)
                fila_consumo['datos'].append("%.2f" % consumo_aparente)
            disponibilidades.append(fila_disp)
            consumos.append(fila_consumo)
    elif ano_inicial:
        poblacion = Poblacion.objects.filter(ano=ano_inicial).aggregate(total=Sum('total_ambos_sexos'))
        fila_disp = {'ano': ano_inicial, 'datos': []}
        fila_consumo = {'ano': ano_inicial, 'datos': []}
        for producto in productos:
            dependencia = DependenciaAlimentaria.objects.get(ano=ano_inicial, producto=producto)
            disponibilidad = dependencia.produccion + dependencia.importaciones + dependencia.donaciones - dependencia.exportaciones
            consumo_aparente = disponibilidad/poblacion['total']
            fila_disp['datos'].append(disponibilidad)
            fila_consumo['datos'].append("%.2f" % consumo_aparente)
        disponibilidades.append(fila_disp)
        consumos.append(fila_consumo)
    else:
        try:
            for ano in rango_anos:
                poblacion = Poblacion.objects.filter(ano=ano).aggregate(total=Sum('total_ambos_sexos'))
                fila_disp = {'ano': ano, 'datos': []}
                fila_consumo = {'ano': ano, 'datos': []}
                for producto in productos:
                    dependencia = DependenciaAlimentaria.objects.get(ano=ano, producto=producto)
                    disponibilidad = dependencia.produccion + dependencia.importaciones + dependencia.donaciones - dependencia.exportaciones
                    consumo_aparente = disponibilidad/poblacion['total']
                    fila_disp['datos'].append(disponibilidad)
                    fila_consumo['datos'].append("%.2f" % consumo_aparente)
                disponibilidades.append(fila_disp)
                consumos.append(fila_consumo)
        except: 
            pass

    #variaciones!
    variacion_disp = []
    variacion_consumo = []
    tope = len(consumos)-1
    for i in range(len(productos)):
        try:
            var_disp = ((float(disponibilidades[tope]['datos'][i]) - float(disponibilidades[0]['datos'][i]))/float(disponibilidades[0]['datos'][i]))*100
            variacion_disp.append("%.2f" % var_disp)
            var_consumos = ((float(consumos[tope]['datos'][i]) - float(consumos[0]['datos'][i]))/float(consumos[0]['datos'][i]))*100
            variacion_consumo.append("%.2f" % var_consumos)
        except:
            pass
            
    dicc = {'disponibilidades': disponibilidades, 'consumos': consumos, 
            'productos': productos, 'var_disp': variacion_disp, 'var_consumos': variacion_consumo, 
            'anos': rango_anos, 'productos_all': productos_all}
    return dicc

def apertura_comercial(request, ano_inicial=None, ano_final=None):
    dicc = __apertura_comercial__(request, ano_inicial, ano_final)
    return render_to_response('seguridad_alimentaria/apertura_comercial.html', dicc)

def grafo_apertura_comercial(request, ano_inicial=None, ano_final=None):
    dicc = __apertura_comercial__(request, ano_inicial, ano_final)
    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis=ano_inicial
    else:
        axis = dicc['anos']

    data = [float(foo['tasa']) for foo in dicc['resultados']]
    message = 'Apertura Comercial'
    legends = ["tasa apertura comercial"]

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart) 

def __apertura_comercial__(request, ano_inicial=None, ano_final=None):
    try:
        anos = AperturaComercial.objects.all().aggregate(maximo=Max('ano'), minimo=Min('ano'))
        rango_anos = range(anos['minimo'], anos['maximo']+1)
    except:
        rango_anos = None

    resultados = [] 

    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            fila = {'ano': ano, 'tasa': None}
            apertura = AperturaComercial.objects.get(ano=ano)
            tasa = ((apertura.exportaciones/apertura.pib) + (apertura.importaciones/apertura.pib)) / 100
            fila['tasa'] = tasa
            resultados.append(fila)
    elif ano_inicial:
        fila = {'ano': ano_inicial, 'tasa': None}
        apertura = AperturaComercial.objects.get(ano=ano_inicial)
        tasa = ((apertura.exportaciones/apertura.pib) + (apertura.importaciones/apertura.pib)) / 100
        fila['tasa'] = tasa
        resultados.append(fila)
    else:
        try:
            for ano in rango_anos:
                fila = {'ano': ano, 'tasa': None}
                apertura = AperturaComercial.objects.get(ano=ano)
                tasa = ((apertura.exportaciones/apertura.pib) + (apertura.importaciones/apertura.pib)) / 100
                fila['tasa'] = tasa
                resultados.append(fila)
        except:
            pass

    #variaciones
    try:
        tope = len(resultados) - 1
        variacion = ((resultados[tope]['tasa'] - resultados[0]['tasa'])/resultados[0]['tasa'])*100 if resultados[0]['tasa']!=0 else 100
    except:
        variacion = 0

    dicc = {'resultados': resultados, 'anos': rango_anos, 'variacion': variacion}
    return dicc
