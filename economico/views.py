from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from models import *
from resources import convertir_mes
from django.template.defaultfilters import slugify
from django.db.models import Avg, Min, Max, Sum
from utils.pygooglechart import SimpleLineChart
from utils import grafos
from django.utils import simplejson
from django.http import HttpResponse
#from forms import AnoFilterForm

def index(request):
    return render_to_response('economico/index.html')

def salario_minimo(request, ano_inicial=None, ano_final=None, sector=None):
    dicc = __salario_minimo__(request, ano_inicial, ano_final, sector)
    return render_to_response('economico/salario_minimo.html', dicc)

def grafo_salario_minimo(request, ano_inicial=None, ano_final=None, sector=None):
    #grafico de lineas
    dicc = __salario_minimo__(request, ano_inicial, ano_final, sector)
    legends = [sector.nombre for sector in dicc['sectores']]
    message = 'Grafico de Salario Minimo'
    
    rows_2_column = []
    for sector in dicc['sectores']:
        rows_2_column.append([])

    for row in dicc['datos']:
        for i in range(len(row['datos'])):
            rows_2_column[i].append(float(row['datos'][i]))
    
    data = [row for row in rows_2_column]
    
    if not dicc['tiene_mes']:
        if ano_inicial and ano_final:
            axis = range(int(ano_inicial), int(ano_final)+1)
        elif ano_inicial:
            axis=ano_inicial
        else:
            axis = dicc['rango']
    else:
        axis = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago',
                'Sep', 'Oct', 'Nov', 'Dic']

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart, multiline=True)
    
def __salario_minimo__(request, ano_inicial=None, ano_final=None, sector=None):
    rango = SalarioMinimo.objects.all().aggregate(minimo=Min('ano'), maximo=Max('ano'))
    sectores_all = Sector.objects.all()
    try:
        rango_anos = range(rango['minimo'], rango['maximo']+1)
    except:
        rango_anos=None
    mes = False
    if sector:
        sector = get_object_or_404(Sector, slug=sector)
        sectores = [sector]
    else:
        sectores = sectores_all 

    resultados = [] 
    promedios = []

    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            fila = {'ano':ano ,'datos': []}
            for sector in sectores:
                try:
                    salario = SalarioMinimo.objects.filter(ano=ano, sector=sector).aggregate(valor=Avg('salario'))
                    tmp = salario['valor']
                    fila['datos'].append("%.2f" % tmp)
                except:
                    fila['datos'].append(0)
            resultados.append(fila)
            
    elif ano_inicial:
        fila = {'ano': ano_inicial, 'mes':0, 'datos': []}
        mes = True
        for sector in sectores:
            promedio = SalarioMinimo.objects.filter(ano=ano_inicial, sector=sector).aggregate(prom=Avg('salario'))
            promedios.append(promedio['prom'])

        for i in range(1,13):
            fila['mes'] = convertir_mes(i)
            fila['datos']=[]
            for sector in sectores:
                try:
                    dato = SalarioMinimo.objects.get(ano=ano_inicial, mes=i, sector=sector)
                    fila['datos'].append(dato.salario)
                except:
                    fila['datos'].append(0)
            temp = dict.copy(fila)
            resultados.append(temp)
    else:
        try:
            for ano in rango_anos:
                fila = {'ano':ano ,'datos': []}
                for sector in sectores:
                    try:
                        salario = SalarioMinimo.objects.filter(ano=ano, sector=sector).aggregate(valor=Avg('salario'))
                        tmp = salario['valor']
                        fila['datos'].append("%.2f" % tmp)
                    except:
                        fila['datos'].append(0)
                resultados.append(fila)
        except TypeError:
                fila = {'ano':0 ,'datos': []}
    
    #variaciones
    variaciones = []
    if fila.has_key('mes')==False:
        tope = len(resultados)-1
        for i in range(len(sectores)):
            try:
                variacion = ((float(resultados[tope]['datos'][i]) - float(resultados[0]['datos'][i]))/float(resultados[0]['datos'][i])*100) if resultados[0]['datos'][i]!= None else 0
            except:
                variacion = 0
            variaciones.append("%.2f" % variacion)
    
    dicc = {'datos': resultados, 'sectores': sectores, 'rango': rango_anos, 'sectores_all': sectores_all,
            'variaciones': variaciones, 'tiene_mes': mes, 'promedios': promedios}
    return dicc

def empleo(resquest, ano_inicial=None, ano_final=None):
    dicc = __empleo__(resquest, ano_inicial, ano_final)
    return render_to_response("economico/empleo.html", dicc)
    
def __empleo__(resquest, ano_inicial=None, ano_final=None):
    anos = FuerzaTrabajo.objects.all().aggregate(minimo = Min('ano'), maximo = Max('ano'))
    try:
        rango_anos = range(int(anos['minimo']), int(anos['maximo'])+1)
    except:
        rango_anos = None

    if ano_inicial and ano_final:
        #rango de aos
        datos = FuerzaTrabajo.objects.filter(ano__range=(ano_inicial, ano_final))
        mensaje = 'Empleo (%s-%s)'  % (ano_inicial, ano_final)
    elif ano_inicial:
        #ano especifico
        datos = FuerzaTrabajo.objects.filter(ano=ano_inicial)
        mensaje = 'Empleo (%s)' % ano_inicial
    else:
        #todos los anos
        #sacar ano max y ano min!
        datos = FuerzaTrabajo.objects.all()
        mensaje = 'Empleo ' 

    pea_poblacion = []  #PEA/Poblacion
    tasa_de_ocupacion = []#total_ocupados/total PEA
    tasa_de_desempleo = []  #100-tasa ocupacion || desempleo abierto/poblacion
    tasa_sub_empleo = [] #sabra Dios...

    for dato in datos:
        calc_pea_poblacion = (float(dato.pea_general)/dato.poblacion_total)*100 
        pea_poblacion.append("%.2f" % calc_pea_poblacion)
        calc_tasa_de_ocupacion = (float(dato.total_ocupados)/dato.pea_general) * 100
        tasa_de_ocupacion.append("%.2f" % calc_tasa_de_ocupacion)
        calc_tasa_de_desempleo = 100-calc_pea_poblacion
        tasa_de_desempleo.append("%.2f" % calc_tasa_de_desempleo)
        #calc_tasa_sub_empleo = #???
        #tasa_sub_empleo.append("%.2f" % calc_tasa_sub_empleo)
    
    dicc = {'datos': datos, 'pea_poblacion': pea_poblacion, 
            'tasa_de_ocupacion': tasa_de_ocupacion, 'tasa_de_desempleo': tasa_de_desempleo,
            'tasa_sub_empleo': tasa_sub_empleo, 'anos': rango_anos, 'mensaje': mensaje}
    return dicc

def canasta_basica(request, tipo=None, ano_inicial=None, ano_final=None):
    dicc = __canasta_basica__(request, tipo, ano_inicial, ano_final)
    template_name = dicc['template']
    del(dicc['template'])
    return render_to_response(template_name, dicc)

def grafo_canasta_basica(request, tipo=None, ano_inicial=None, ano_final=None):
    dicc = __canasta_basica__(request, tipo, ano_inicial, ano_final)
    legends = dicc['columnas'] 
    message = 'Grafico de Canasta Basica'
    
    rows_2_column = []
    for sector in dicc['columnas']:
        rows_2_column.append([])

    for row in dicc['datos']:
        for i in range(len(row['datos'])):
            try:
                rows_2_column[i].append(float(row['datos'][i]))
            except:
                rows_2_column[i].append(0)
    
    data = [row for row in rows_2_column]
    
    if ano_inicial and ano_final:
        axis = range(int(ano_inicial), int(ano_final)+1)
    elif ano_inicial:
        axis=ano_inicial
    else:
        axis = dicc['rango']
        #axis = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago',
        #        'Sep', 'Oct', 'Nov', 'Dic']

    return grafos.make_graph(data, legends, message, axis, type=SimpleLineChart, multiline=True)
    
def __canasta_basica__(request, tipo=None, ano_inicial=None, ano_final=None):
    columnas = []
    anos = CanastaBasica.objects.all().aggregate(maximo=Max('ano'), minimo=Min('ano'))
    try:
        rango_anos = range(anos['minimo'], anos['maximo']+1)
    except:
        rango_anos = None

    tipos_all = TipoCanastaBasica.objects.all()

    if tipo:
        tipo = get_object_or_404(TipoCanastaBasica, slug__iexact=tipo)
        tipos = [tipo]
    else:
        tipos = tipos_all

    resultados = []
    template_name = 'economico/canasta_basica.html'
    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            filita = {'ano': ano, 'datos': []}
            for tipo in tipos:
                canastas = CanastaBasica.objects.filter(ano=ano, tipo=tipo).aggregate(costo=Avg('costo'))
                filita['datos'].append(canastas['costo'])
            resultados.append(filita)
    elif ano_inicial:
        filita = {'ano': ano_inicial,'mes': 0, 'datos': []}
        for i in range(1,13):
            filita['mes']=convertir_mes(i)
            filita['datos'] = []
            for tipo in tipos:
                try:
                    canastas = CanastaBasica.objects.get(ano=ano_inicial, tipo=tipo, mes=i)
                    filita['datos'].append(canastas.costo)
                except:
                    filita['datos'].append(0)
            temp = dict.copy(filita)#para romper la byref
            resultados.append(temp)
        template_name='economico/canasta_basica_mes.html'
    else:
        try:
            for ano in rango_anos:
                filita = {'ano': ano, 'datos': []}
                for tipo in tipos:
                    canastas = CanastaBasica.objects.filter(ano=ano, tipo=tipo).aggregate(costo=Avg('costo'))
                    filita['datos'].append(canastas['costo'])
                resultados.append(filita)
        except TypeError:
            pass
    
    variaciones = [] 
    for tipo in tipos:
        columnas.append(tipo.tipo)

    tope = len(resultados)-1
    for i in range(len(tipos)):
        #variaciones
        try:
            variacion = ((resultados[tope]['datos'][i] - resultados[0]['datos'][i])/ resultados[0]['datos'][i])*100
            variaciones.append(variacion)
        except:
            variaciones.append(0)
        
    dicc = {'datos':resultados, 'columnas': columnas, 'variaciones': variaciones,
            'tipos_all': tipos_all, 'rango': rango_anos, 'template': template_name}
    return dicc

def mercados(request, departamento=None, municipio=None):
    dicc = __mercados__(request, departamento, municipio)
    return render_to_response("economico/mercados.html", dicc)

def __mercados__(request, departamento=None, municipio=None):
    departamentos = Departamento.objects.all()
    if departamento:
        datos = get_list_or_404(Mercado, departamento__id=departamento)
        mensaje = "Mercados del departamento de %s" % datos[0].departamento.nombre
    elif municipio:
        datos = get_list_or_404(Mercado, municipio__id=municipio)
        mensaje = "Mercados del municipio de %s" % datos[0].municipio.nombre
    else:
        datos = Mercado.objects.all()
        mensaje="Todos los mercados"

    dicc = {'mercados': datos, 'mensaje': mensaje, 'departamentos': departamentos}
    return dicc

def salario_nominal_real(request, ano_inicial=None, ano_final=None):
    dicc = __salario_nominal_real__(request, ano_inicial, ano_final)
    return render_to_response('economico/salario_nominal_real.html', dicc)

def grafo_salario_nominal_real(request, ano_inicial=None, ano_final=None):
    dicc = __salario_nominal_real__(request, ano_inicial, ano_final)
    rows_nominal = [[],[],[]]
    rows_real = [[],[],[]]
    
    legends = ['Gobierno Central', 'Salario Nacional', 'Asegurados INSS']

    if not dicc['tiene_mes']:
        if ano_inicial and ano_final:
            axis = range(int(ano_inicial), int(ano_final)+1)
        elif ano_inicial:
            axis=ano_inicial
        else:
            axis = dicc['anos']
    else:
        axis = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago',
                'Sep', 'Oct', 'Nov', 'Dic']

    for row in dicc['datos']:
        for i in range(0,3):
            try:
                rows_nominal[i].append(float(row['datos'][i]))
            except:
                rows_nominal[i].append(0)
            try:
                rows_real[i].append(float(row['datos'][i+3]))
            except:
                rows_real[i].append(0)
    
    data_nominal = [row for row in rows_nominal]
    data_real = [row for row in rows_real]
    
    message = "Salario Nominal"
    try:
        url_nominal = grafos.make_graph(data_nominal, legends, message, 
                                        axis, type=SimpleLineChart, multiline=True, return_json=False)
    except:
        url_nominal=None
    message = "Salario Real"
    try:
        url_real= grafos.make_graph(data_real, legends, message,
                                    axis, type=SimpleLineChart, multiline=True, return_json=False)
    except:
        url_real = None

    json_dicc = {'url_nominal': url_nominal, 'url_real': url_real}
    return HttpResponse(simplejson.dumps(json_dicc), mimetype="application/javascript")

def __salario_nominal_real__(request, ano_inicial=None, ano_final=None):
    mes = False
    resultados = [] 

    rango_nominal = SalarioNominal.objects.all().aggregate(minimo=Min('ano'), maximo=Max('ano'))
    rango_real = SalarioNominal.objects.all().aggregate(minimo=Min('ano'), maximo=Max('ano'))
    rango = {'minimo':0, 'maximo':0}

    if rango_nominal['minimo'] == None and rango_nominal['maximo']==None:
        rango_nominal={'minimo': 0, 'maximo': 0}
    if rango_real['minimo'] == None and rango_real['maximo']==None:
        rango_real={'minimo': 0, 'maximo': 0}

    if rango_nominal['minimo']<=rango_real['minimo']:
        rango['minimo']=rango_nominal['minimo']
    else:
        rango['minimo']=rango_real['minimo']

    if rango_nominal['maximo']<=rango_real['maximo']:
        rango['maximo']=rango_nominal['maximo']
    else:
        rango['maximo']=rango_real['maximo']
    
    rango_anos = range(rango['minimo'], rango['maximo']+1)


    if ano_inicial and ano_final:
        for ano in range(int(ano_inicial), int(ano_final)+1):
            fila = {'ano':ano ,'datos': []}
            try:
                salario_nominal = SalarioNominal.objects.filter(ano=ano).aggregate(asegurados=Avg('asegurados_inss'),
                                                                                   gobierno=Avg('gobierno_central'),
                                                                                   nacional=Avg('salario_nacional'))
                fila['datos'].append(salario_nominal['asegurados'])
                fila['datos'].append(salario_nominal['gobierno'])
                fila['datos'].append(salario_nominal['nacional'])
            except:
                salario_nominal = {'asegurados': 0, 'gobierno': 0, 'nacional':0}
                for key in salario_nominal.keys():
                    fila['datos'].append(0)
                
            try:
                salario_real= SalarioReal.objects.filter(ano=ano).aggregate(asegurados=Avg('asegurados_inss'),
                                                                                           gobierno=Avg('gobierno_central'),
                                                                                           nacional=Avg('salario_nacional'))
                fila['datos'].append(salario_real['asegurados'])
                fila['datos'].append(salario_real['gobierno'])
                fila['datos'].append(salario_real['nacional'])
            except:
                salario_real = {'asegurados': 0, 'gobierno': 0, 'nacional':0}
                for key in salario_real.keys():
                    fila['datos'].append(0)

            #variaciones del salario real 
            for key in salario_nominal.keys():
                variacion = ((salario_nominal[key] - salario_real[key])/salario_nominal[key])*100
                fila['datos'].append(variacion)
            temp = dict.copy(fila)
            resultados.append(temp)
            
    elif ano_inicial:
        fila = {'ano': ano_inicial, 'mes':0, 'datos': []}
        mes = True
        for i in range(1,13):
            fila['mes'] = convertir_mes(i)
            fila['datos']=[]
            try:
                dato_nominal = SalarioNominal.objects.get(ano=ano_inicial, mes=i)
                fila['datos'].append(dato_nominal.asegurados_inss)
                fila['datos'].append(dato_nominal.gobierno_central)
                fila['datos'].append(dato_nominal.salario_nacional)
            except:
                dato_nominal=None
                fila['datos'].append(0)
                fila['datos'].append(0)
                fila['datos'].append(0)
            try:
                dato_real = SalarioReal.objects.get(ano=ano_inicial, mes=i)
                fila['datos'].append(dato_real.asegurados_inss)
                fila['datos'].append(dato_real.gobierno_central)
                fila['datos'].append(dato_real.salario_nacional)
            except:
                dato_real = None
                fila['datos'].append(0)
                fila['datos'].append(0)
                fila['datos'].append(0)
            #variaciones
            try:
                variacion_inss = ((dato_nominal.asegurados_inss - dato_real.asegurados_inss)/dato_nominal.asegurados_inss)*100
                fila['datos'].append(variacion_inss)
            except:
                fila['datos'].append(0)
            try:
                variacion_central= ((dato_nominal.gobierno_central- dato_real.asegurados_inss)/dato_nominal.asegurados_inss)*100
                fila['datos'].append(variacion_central)
            except:
                fila['datos'].append(0)
            try:
                variacion_nacional= ((dato_nominal.salario_nacional- dato_real.salario_nacional)/dato_nominal.salario_nacional)*100
                fila['datos'].append(variacion_nacional)
            except:
                fila['datos'].append(0)
            
            temp = dict.copy(fila)
            resultados.append(temp)
    else:
        for ano in rango_anos: 
            fila = {'ano':ano ,'datos': []}
            try:
                salario_nominal = SalarioNominal.objects.filter(ano=ano).aggregate(asegurados=Avg('asegurados_inss'), 
                                                                                                 gobierno=Avg('gobierno_central'),
                                                                                                 nacional=Avg('salario_nacional'))
                for key in salario_nominal.keys():
                    fila['datos'].append(salario_nominal[key])
            except:
                salario_nominal = {'asegurados': 0, 'gobierno': 0, 'nacional':0}
                for key in salario_nominal.keys():
                    fila['datos'].append(0)
                
            try:
                salario_real= SalarioReal.objects.filter(ano=ano).aggregate(asegurados=Avg('asegurados_inss'),
                                                                                           gobierno=Avg('gobierno_central'),
                                                                                           nacional=Avg('salario_nacional'))
                for key in salario_real.keys():
                    fila['datos'].append(salario_real[key])
            except:
                salario_real = {'asegurados': 0, 'gobierno': 0, 'nacional':0}
                for key in salario_real.keys():
                    fila['datos'].append(0)
            #variaciones del salario real 
            for key in salario_nominal.keys():
                try:
                    variacion = ((salario_nominal[key] - salario_real[key])/salario_nominal[key])*100
                except TypeError:
                    variacion = 0
                fila['datos'].append(variacion)
            temp = dict.copy(fila)
            resultados.append(temp)
        

    #variaciones
    variaciones = []
    if fila.has_key('mes')==False:
        tope = len(resultados)-1
        for i in range(len(resultados[0]['datos'])):
            try:
                variacion = ((float(resultados[tope]['datos'][i]) - 
                              float(resultados[0]['datos'][i]))/float(resultados[0]['datos'][i])*100) 
            except:
                variacion=0
            variaciones.append(variacion)
    
    dicc = {'datos': resultados, 'variaciones': variaciones,
            'tiene_mes': mes, 'anos': rango_anos}
    return dicc
