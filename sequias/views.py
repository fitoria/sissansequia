# -*- coding: UTF-8 -*-
 
from django.shortcuts import render_to_response
from models import Encuesta
from forms import *
from lugar.models import *
from django.conf import settings
from django.db.models import Sum, Count, Avg
from django.utils import simplejson
from decimal import Decimal
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseBadRequest
from decorators import session_required
from django.views.decorators.cache import cache_page
from django.template.loader import get_template
from django.template import Context
from utils.pygooglechart import PieChart3D, GroupedVerticalBarChart
from utils import grafos
import ho.pisa as pisa
import cStringIO as StringIO
import cgi

GRAFO_SIZE=(320, 250)

def index(request):
    return render_to_response('base.html')

def consultar(request):
    if request.method=='POST':
        mensaje = None
        form = SequiaForm(request.POST)
        if form.is_valid():
            request.session['fecha_inicio'] = form.cleaned_data['fecha_inicio']
            request.session['fecha_final'] = form.cleaned_data['fecha_final'] 
            request.session['departamento'] = form.cleaned_data['departamento']
            try:
                municipio = Municipio.objects.get(id=form.cleaned_data['municipio']) 
            except:
                municipio = None
            try:
                comunidad = Comunidad.objects.get(id=form.cleaned_data['comunidad']) 
            except:
                comunidad = None
            try:
                entrevistado = Entrevistado.objects.get(id=form.cleaned_data['entrevistado'])
            except:
                entrevistado= None
            request.session['municipio'] = municipio 
            request.session['comunidad'] = comunidad
            request.session['entrevistado'] = entrevistado
            mensaje = "Explore los resultos en el menu superior"
            request.session['activo'] = True 
    else:
        form = SequiaForm()
        mensaje = "" 
#    dict = {'form': form, 'mensaje': mensaje,'user': request.user}
#    return direct_to_template(request, 'index.html', dict)
    return render_to_response("index.html", locals())

def get_municipios(request, departamento):
    municipios = Municipio.objects.filter(departamento = departamento)
    lista = [(municipio.id, municipio.nombre) for municipio in municipios]
    return HttpResponse(simplejson.dumps(lista), mimetype='application/javascript')

def get_comunidad(request, municipio):
    comunidades = Comunidad.objects.filter(municipio = municipio )
    lista = [(comunidad.id, comunidad.nombre) for comunidad in comunidades]
    return HttpResponse(simplejson.dumps(lista), mimetype='application/javascript')

def get_entrevista(request, comunidad):
    entrevistados = Entrevistado.objects.filter(comunidad = comunidad )
    lista = [(entrevista.id, entrevista.nombre) for entrevista in entrevistados]
    return HttpResponse(simplejson.dumps(lista), mimetype='application/javascript')

#Vista para la perdida de la cosecha primera, postrera y apante
@session_required
def perdidapostrera(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado'].id
        perdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        perdida = Encuesta.objects.all()
        
    casos = perdida.count()
    #TODO: Sumatorias de maiz,frijol,sorgo CICLO PRIMERA
    # 2=Maiz, 3=Frijol, 4=sorgo
    sorgo_planea = perdida.filter(primera__producto__id=4).aggregate(Sum('primera__planea_siembra'))['primera__planea_siembra__sum']
    arroz_sembrada = perdida.filter(primera__producto__id=4).aggregate(Sum('primera__area_sembrada'))['primera__area_sembrada__sum']
    #----------
    frijol_planea = perdida.filter(primera__producto__id=3).aggregate(Sum('primera__planea_siembra'))['primera__planea_siembra__sum']
    frijol_sembrada = perdida.filter(primera__producto__id=3).aggregate(Sum('primera__area_sembrada'))['primera__area_sembrada__sum']
    #------------
    maiz_planea = perdida.filter(primera__producto__id=2).aggregate(Sum('primera__planea_siembra'))['primera__planea_siembra__sum']
    maiz_sembrada = perdida.filter(primera__producto__id=2).aggregate(Sum('primera__area_sembrada'))['primera__area_sembrada__sum']
    #TODO: area cosechada
    arroz_cosechada = perdida.filter(primera__producto__id=4).aggregate(Sum('primera__area_cosechada'))['primera__area_cosechada__sum']
    frijol_cosechada = perdida.filter(primera__producto__id=3).aggregate(Sum('primera__area_cosechada'))['primera__area_cosechada__sum']
    maiz_cosechada = perdida.filter(primera__producto__id=2).aggregate(Sum('primera__area_cosechada'))['primera__area_cosechada__sum']
    #TODO:area perdida
    try:
        arroz_perdida = (arroz_sembrada - arroz_cosechada)
    except:
        pass
    try:
        frijol_perdida = (frijol_sembrada - frijol_cosechada)
    except:
        pass
    try:
        maiz_perdida = (maiz_sembrada - maiz_cosechada)
    except:
        pass
    #TODO: produccion
    arroz_produccion = perdida.filter(primera__producto__id=4).aggregate(Sum('primera__produccion'))['primera__produccion__sum']
    frijol_produccion = perdida.filter(primera__producto__id=3).aggregate(Sum('primera__produccion'))['primera__produccion__sum']
    maiz_produccion = perdida.filter(primera__producto__id=2).aggregate(Sum('primera__produccion'))['primera__produccion__sum']
    #TODO: rendimientos
    try:
        arroz_rendi = arroz_produccion / arroz_cosechada
    except:
        pass
    try:
        frijol_rendi = frijol_produccion / frijol_cosechada
    except:
        pass
    try:
        maiz_rendi = maiz_produccion / maiz_cosechada
    except:
        pass
    
    #TODO: CICLO POSTRERA, arroz=sorgo :) :P
    sorgo_planea_p = perdida.filter(postrera__producto__id=4).aggregate(Sum('postrera__planea_siembra'))['postrera__planea_siembra__sum']
    arroz_sembrada_P = perdida.filter(postrera__producto__id=4).aggregate(Sum('postrera__area_sembrada'))['postrera__area_sembrada__sum']
    #---------
    frijol_planea_p = perdida.filter(postrera__producto__id=3).aggregate(Sum('postrera__planea_siembra'))['postrera__planea_siembra__sum']
    frijol_sembrada_P = perdida.filter(postrera__producto__id=3).aggregate(Sum('postrera__area_sembrada'))['postrera__area_sembrada__sum']
    #-----------
    maiz_planea_p = perdida.filter(postrera__producto__id=2).aggregate(Sum('postrera__planea_siembra'))['postrera__planea_siembra__sum']
    maiz_sembrada_P = perdida.filter(postrera__producto__id=2).aggregate(Sum('postrera__area_sembrada'))['postrera__area_sembrada__sum'] 
    #TODO: area cosechada
    arroz_cosechada_P = perdida.filter(postrera__producto__id=4).aggregate(Sum('postrera__area_cosechada'))['postrera__area_cosechada__sum']
    frijol_cosechada_P = perdida.filter(postrera__producto__id=3).aggregate(Sum('postrera__area_cosechada'))['postrera__area_cosechada__sum']
    maiz_cosechada_P = perdida.filter(postrera__producto__id=2).aggregate(Sum('postrera__area_cosechada'))['postrera__area_cosechada__sum']
    #TODO:area perdida
    try:
        arroz_perdida_P = arroz_sembrada_P - arroz_cosechada_P
    except:
        pass
    try:
        frijol_perdida_P = frijol_sembrada_P - frijol_cosechada_P
    except:
        pass
    try:
        maiz_perdida_P = maiz_sembrada_P - maiz_cosechada_P
    except:
        pass
    #TODO: produccion
    arroz_produccion_P = perdida.filter(postrera__producto__id=4).aggregate(Sum('postrera__produccion'))['postrera__produccion__sum']
    frijol_produccion_P = perdida.filter(postrera__producto__id=3).aggregate(Sum('postrera__produccion'))['postrera__produccion__sum']
    maiz_produccion_P = perdida.filter(postrera__producto__id=2).aggregate(Sum('postrera__produccion'))['postrera__produccion__sum']
    #TODO: rendimientos
    try:
        arroz_rendi_P = arroz_produccion_P / arroz_cosechada_P
    except:
        pass
    try:
        frijol_rendi_P = frijol_produccion_P / frijol_cosechada_P
    except:
        pass
    try:
        maiz_rendi_P = maiz_produccion_P / maiz_cosechada_P
    except:
        pass
        
    #Ciclo Apante
    sorgo_planea_a = perdida.filter(apante__producto__id=4).aggregate(Sum('apante__planea_siembra'))['apante__planea_siembra__sum']
    arroz_sembrada_A = perdida.filter(apante__producto__id=4).aggregate(Sum('apante__area_sembrada'))['apante__area_sembrada__sum']
    #------------
    frijol_planea_a = perdida.filter(apante__producto__id=3).aggregate(Sum('apante__planea_siembra'))['apante__planea_siembra__sum']
    frijol_sembrada_A = perdida.filter(apante__producto__id=3).aggregate(Sum('apante__area_sembrada'))['apante__area_sembrada__sum']
    #-------------
    maiz_planea_a = perdida.filter(apante__producto__id=2).aggregate(Sum('apante__planea_siembra'))['apante__planea_siembra__sum']
    maiz_sembrada_A = perdida.filter(apante__producto__id=2).aggregate(Sum('apante__area_sembrada'))['apante__area_sembrada__sum']
    #TODO: area cosechada
    arroz_cosechada_A = perdida.filter(apante__producto__id=4).aggregate(Sum('apante__area_cosechada'))['apante__area_cosechada__sum']
    frijol_cosechada_A = perdida.filter(apante__producto__id=3).aggregate(Sum('apante__area_cosechada'))['apante__area_cosechada__sum']
    maiz_cosechada_A = perdida.filter(apante__producto__id=2).aggregate(Sum('apante__area_cosechada'))['apante__area_cosechada__sum']
    #TODO:area perdida
    try:
        arroz_perdida_A = (arroz_sembrada_A - arroz_cosechada_A)
    except:
        pass
    try:
        frijol_perdida_A = (frijol_sembrada_A - frijol_cosechada_A)
    except:
        pass
    try:
        maiz_perdida_A = (maiz_sembrada_A - maiz_cosechada_A)
    except:
        pass
    #TODO: produccion
    arroz_produccion_A = perdida.filter(apante__producto__id=4).aggregate(Sum('apante__produccion'))['apante__produccion__sum']
    frijol_produccion_A = perdida.filter(apante__producto__id=3).aggregate(Sum('apante__produccion'))['apante__produccion__sum']
    maiz_produccion_A = perdida.filter(apante__producto__id=2).aggregate(Sum('apante__produccion'))['apante__produccion__sum']
    #TODO: rendimientos
    try:
        arroz_rendi_A = arroz_produccion_A / arroz_cosechada_A
    except:
        pass
    try:
        frijol_rendi_A = frijol_produccion_A / frijol_cosechada_A
    except:
        pass
    try:
        maiz_rendi_A = maiz_produccion_A / maiz_cosechada_A
    except:
        pass
    
    return render_to_response("encuesta/perdida.html", locals())

@session_required    
def disponibilidad(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado'].id
        dispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        dispo = Encuesta.objects.all()
        
    casos = dispo.count()
    #TODO: sumas de toda la tabla disponibilidad
    total_adulto= dispo.aggregate(Sum('disponibilidad__adultos_casa'))['disponibilidad__adultos_casa__sum']
    total_ninos=dispo.aggregate(Sum('disponibilidad__ninos_casa'))['disponibilidad__ninos_casa__sum']
    total_vacas = dispo.aggregate(Sum('disponibilidad__vacas'))['disponibilidad__vacas__sum']
    total_cerdos = dispo.aggregate(Sum('disponibilidad__cerdos'))['disponibilidad__cerdos__sum']
    total_gallinas =dispo.aggregate(Sum('disponibilidad__gallinas'))['disponibilidad__gallinas__sum']
    total_maiz=dispo.aggregate(Sum('disponibilidad__maiz_disponible'))['disponibilidad__maiz_disponible__sum']
    total_frijol=dispo.aggregate(Sum('disponibilidad__frijol_disponible'))['disponibilidad__frijol_disponible__sum']
    total_sorgo=dispo.aggregate(Sum('disponibilidad__sorgo_disponible'))['disponibilidad__sorgo_disponible__sum']
    try:
        prom_maiz=total_maiz/casos
    except:
        pass
    try:
        prom_frijol=total_frijol/casos
    except:
        pass
    try:
        prom_sorgo=total_sorgo/casos
    except:
        pass
    try:
        criterio1 = (float(total_maiz) * 100) / ((float(total_adulto) * 1) + (float(total_ninos) * 0.9))
    except:
        pass
    try:
        criterio2 = (float(total_frijol) * 100) / ((float(total_adulto) * 0.5) + (float(total_ninos) * 0.4))
    except:
        pass
    try:
        criterio3 = ((float(total_maiz) + float(total_sorgo)) * 100) / ((float(total_adulto) * 1) + (float(total_ninos) * 0.9) + (total_cerdos * 2.5)+(total_gallinas * 0.156))
    except:
        pass
    
    return render_to_response("encuesta/disponibilidad.html", locals())

@session_required
def nutricion(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado'].id
        nutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        nutri = Encuesta.objects.all()
        
    casos = nutri.count()
    # niños de 1-5 años
    ninos_normal = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=1).count()
    ninos_riesgo = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=4).count()
    ninos_desnutrido = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=3).count()
    ninos_nosabe = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=5).count()
        #rango 6-10
    ninos_normal_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=1).count()
    ninos_riesgo_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=4).count()
    ninos_desnutrido_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=3).count()
    ninos_nosabe_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=5).count()
        #rango mayor 11
    ninos_normal_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=1).count()
    ninos_riesgo_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=4).count()
    ninos_desnutrido_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=3).count()
    ninos_nosabe_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninos",  nutricion__brazalete__id=5).count()
    #ahora vamos con las niñas :)
    ninas_normal = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=1).count()
    ninas_riesgo = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=4).count()
    ninas_desnutrido = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=3).count()
    ninas_nosabe = nutri.filter(nutricion__edad__range=(1,5), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=5).count()
        #rango 6-10
    ninas_normal_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=1).count()
    ninas_riesgo_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=4).count()
    ninas_desnutrido_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=3).count()
    ninas_nosabe_s = nutri.filter(nutricion__edad__range=(6,10), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=5).count()
        #rango mayor 11
    ninas_normal_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=1).count()
    ninas_riesgo_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=4).count()
    ninas_desnutrido_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=3).count()
    ninas_nosabe_o = nutri.filter(nutricion__edad__range=(11,15), nutricion__ninos__contains="ninas",  nutricion__brazalete__id=5).count()
    
    
    return render_to_response("encuesta/nutricion.html", locals())

@session_required
def grafo_perdida(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado']
        gperdida = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        gperdida = Encuesta.objects.all()
        
    casos = gperdida.count()
    maiz_s = 0
    maiz_c = 0
    frijol_s = 0
    frijol_c = 0
    sorgo_s = 0
    sorgo_c = 0
    razon1 = 0
    razon2 = 0
    razon3 = 0
    razon4 = 0
    razon5 = 0
    razon6 = 0
    razon7 = 0
    for encuesta in gperdida:
        for primera in encuesta.primera.filter(producto__id=2):
            maiz_s = primera.area_sembrada + maiz_s
            maiz_c = primera.area_cosechada + maiz_c
#    for encuesta in gperdida:
        for primera in encuesta.primera.filter(producto__id=3):
            frijol_s = primera.area_sembrada + frijol_s
            frijol_c = primera.area_cosechada + frijol_c
#    for encuesta in gperdida:
        for primera in encuesta.primera.filter(producto__id=4):
            sorgo_s = primera.area_sembrada + sorgo_s
            sorgo_c = primera.area_cosechada + sorgo_c
    #Razones de perdida primera
    razon1 = gperdida.filter(primera__perdida__id=1).count()
    razon2 = gperdida.filter(primera__perdida__id=2).count()
    razon3 = gperdida.filter(primera__perdida__id=3).count()
#    for encuesta in gperdida:
#        for primera in encuesta.primera.filter(perdida__id=1):
#            razon1 = primera.perdida.id + razon1
#    for encuesta in gperdida:
#        for primera in encuesta.primera.filter(perdida__id=2):
#            razon2 = primera.perdida.id + razon2
#    for encuesta in gperdida:
#        for primera in encuesta.primera.filter(perdida__id=3):
#            razon3 = primera.perdida.id + razon3
    #Esto es para postrera
    maiz_s_P = 0
    maiz_c_P = 0
    frijol_s_P = 0
    frijol_c_P = 0
    sorgo_s_P = 0
    sorgo_c_P = 0
    razon1_p = 0
    razon2_p = 0
    razon3_p = 0
    razon4_p = 0
    razon5_p = 0
    razon6_p = 0
    razon7_p = 0
    for encuesta in gperdida:
        for postrera in encuesta.postrera.filter(producto__id=2):
            maiz_s_P = postrera.area_sembrada + maiz_s_P
            maiz_c_P = postrera.area_cosechada + maiz_c_P
#    for encuesta in gperdida:
        for postrera in encuesta.postrera.filter(producto__id=3):
            frijol_s_P = postrera.area_sembrada + frijol_s_P
            frijol_c_P = postrera.area_cosechada + frijol_c_P
#    for encuesta in gperdida:
        for postrera in encuesta.postrera.filter(producto__id=4):
            sorgo_s_P = postrera.area_sembrada + sorgo_s_P
            sorgo_c_P = postrera.area_cosechada + sorgo_c_P
    #Razones de perdidas postrera
    razon1_p = gperdida.filter(postrera__perdida__id=1).count()
    razon2_p = gperdida.filter(postrera__perdida__id=2).count()
    razon3_p = gperdida.filter(postrera__perdida__id=3).count()
#    for encuesta in gperdida:
#        for postrera in encuesta.postrera.filter(perdida__id=1):
#            razon1_p = primera.perdida.id + razon1_p
#    for encuesta in gperdida:
#        for postrera in encuesta.postrera.filter(perdida__id=2):
#            razon2_p = postrera.perdida.id + razon2_p
#    for encuesta in gperdida:
#        for postrera in encuesta.postrera.filter(perdida__id=3):
#            razon3_p = postrera.perdida.id + razon3_p            
    #Esto es para apante
    maiz_s_A=0
    maiz_c_A=0
    frijol_s_A=0
    frijol_c_A=0
    sorgo_s_A=0
    sorgo_c_A=0
    razon1_A=0
    razon2_A=0
    razon3_A=0
    for encuesta in gperdida:
        for apante in encuesta.apante.filter(producto__id=2):
            try:
                maiz_s_A = apante.area_sembrada + maiz_s_A
                maiz_c_A = apante.area_cosechada + maiz_c_A
            except:
                pass
        for apante in encuesta.apante.filter(producto__id=3):
            try:
                frijol_s_A = apante.area_sembrada + frijol_s_A
                frijol_c_A = apante.area_cosechada + frijol_c_A
            except:
                pass
        for apante in encuesta.apante.filter(producto__id=4):
            try:
                sorgo_s_A = apante.area_sembrada + sorgo_s_A
                sorgo_c_A = apante.area_cosechada + sorgo_c_A
            except:
                pass
    #Razones de perdida apante
    razon1_A = gperdida.filter(apante__perdida__id=1).count()
    razon2_A = gperdida.filter(apante__perdida__id=2).count()
    razon3_A = gperdida.filter(apante__perdida__id=3).count()
    #Calculacion de las perdidas de primera 
    resta = maiz_s - maiz_c
    resta_f = frijol_s - frijol_c
    resta_s = sorgo_s - sorgo_c
    #Calculacion de las perdidas de postrera
    resta_P = maiz_s_P - maiz_c_P
    resta_f_P = frijol_s_P - frijol_c_P
    resta_s_P = sorgo_s_P - sorgo_c_P
    #Claculacion de las perdidas de apante
    resta_A = maiz_s_A - maiz_c_A
    resta_f_A = frijol_s_A - frijol_c_A
    resta_s_A = sorgo_s_A - sorgo_c_A
    
    #Calculacion de los porcentajes de primera
    p_c = (float(maiz_c)) *100
    p_p = (float(resta)) *100
    
    p_c_f = (float(frijol_c)) *100
    p_p_f = (float(resta_f)) *100
    
    p_c_s = (float(sorgo_c)) *100
    p_p_s = (float(resta_s)) *100
    
    p_razon1= (float(razon1)) *100
    p_razon2= (float(razon2)) *100
    p_razon3= (float(razon3)) *100
    #Calculacion de los porcentajes de la Postrera
    p_c_P = (float(maiz_c_P)) *100
    p_p_P = (float(resta_P)) *100
    
    p_c_f_P = (float(frijol_c_P)) *100
    p_p_f_P = (float(resta_f_P)) *100
    
    p_c_s_P = (float(sorgo_c_P)) *100
    p_p_s_P = (float(resta_s_P)) *100
    
    p_razon1_p= (float(razon1_p)) *100
    p_razon2_p= (float(razon2_p)) *100
    p_razon3_p= (float(razon3_p)) *100
    #Calculacion de los porcentajes de Apante
    p_c_A = (float(maiz_c_A)) *100
    p_p_A = (float(resta_A)) *100
    
    p_c_f_A = (float(frijol_c_A)) *100
    p_p_f_A = (float(resta_f_A)) *100
    
    p_c_s_A = (float(sorgo_c_A)) * 100
    p_p_s_A = (float(resta_s_A)) *100
    
    p_razon1_A = (float(razon1_A)) *100
    p_razon2_A = (float(razon2_A)) *100
    p_razon3_A = (float(razon3_A)) *100
    #envios de los datos a utils solo primera
    lista = [p_c,p_p]
    lista1 = [p_c_f,p_p_f]
    lista2 = [p_c_s,p_p_s]
    lista3 = [p_razon1,p_razon2,p_razon3]
    legends = ['Area Cosechada','Area Perdida']
    legends1 = ['Area Cosechada','Area Perdida']
    legends2 = ['Area Cosechada','Area Perdida']
    legends3 = ['Sequia','Mala semilla','plaga']
    mensa = "Grafico Maiz"
    mensa1 = "Grafico Frijol"
    mensa2 = "Grafico Sorgo"
    mensa3 = "Grafico razones de perdida"
    #envios de los datos a utils solo para postrera
    lista_P = [p_c_P,p_p_P]
    lista1_P = [p_c_f_P,p_p_f_P]
    lista2_P = [p_c_s_P,p_p_s_P]
    lista3_P = [p_razon1_p,p_razon2_p,p_razon3_p]
    legends_P = ['Area Cosechada','Area Perdida']
    legends1_P = ['Area Cosechada','Area Perdida']
    legends2_P = ['Area Cosechada','Area Perdida']
    legends3_P = ['Sequia','Mala semilla','plaga']
    mensa_P = "Grafico Maiz"
    mensa1_P = "Grafico Frijol"
    mensa2_P = "Grafico Sorgo"
    mensa3_P = "Grafico razones de perdida"
    #envios de los datos a utils solo para apante
    lista_A = [p_c_A,p_p_A]
    lista1_A = [p_c_f_A,p_p_f_A]
    lista2_A = [p_c_s_A,p_p_s_A]
    lista3_A = [p_razon1_A,p_razon2_A,p_razon3_A]
    legends_A = ['Area Cosechada','Area Perdida']
    legends1_A = ['Area Cosechada','Area Perdida']
    legends2_A = ['Area Cosechada','Area Perdida']
    legends3_A = ['Sequia','Mala semilla','plaga']
    mensa_A = "Grafico Maiz"
    mensa1_A = "Grafico Frijol"
    mensa2_A = "Grafico Sorgo"
    mensa3_A = "Grafico razones de perdida"
    #Envios de las url solo para primera
    url = grafos.make_graph(lista, legends, mensa, return_json=False)
    url1 = grafos.make_graph(lista1, legends1, mensa1, return_json=False)
    url2 = grafos.make_graph(lista2, legends2, mensa2, return_json=False)
    url6 = grafos.make_graph(lista3, legends3, mensa3, return_json=False)
    #Envios de las url solo para postrera
    url3 = grafos.make_graph(lista_P, legends_P, mensa_P, return_json=False)
    url4 = grafos.make_graph(lista1_P, legends1_P, mensa1_P, return_json=False)
    url5 = grafos.make_graph(lista2_P, legends2_P, mensa2_P, return_json=False)
    url7 = grafos.make_graph(lista3_P, legends3_P, mensa3_P, return_json=False)
    #Envios de las url para apante
    url8 = grafos.make_graph(lista_A,legends_A,mensa_A, return_json=False)
    url9 = grafos.make_graph(lista1_A,legends1_A,mensa1_A,return_json=False)
    url10 = grafos.make_graph(lista2_A,legends2_A,mensa2_A,return_json=False)
    url11 = grafos.make_graph(lista3_A,legends3_A,mensa3_A, return_json=False)
    
    
    return render_to_response("encuesta/grafos.html", locals())
                                                       
@session_required
def grafo_nutricion(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado']
        gnutri = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        gnutri = Encuesta.objects.all()
        
    casos = gnutri.count()
#    normal_v = 0
#    desnutrido_v = 0
#    riesgo_v = 0
#    nosabe_v = 0
#    normal_m = 0
#    desnutrido_m = 0
#    riesgo_m = 0
#    nosabe_m = 0
    # solo para niños
    normal_v = gnutri.filter(nutricion__ninos__contains="ninos", nutricion__brazalete__id=1).count()
    desnutrido_v = gnutri.filter(nutricion__ninos__contains="ninos", nutricion__brazalete__id=3).count()
    riesgo_v = gnutri.filter(nutricion__ninos__contains="ninos", nutricion__brazalete__id=4).count()
    nosabe_v = gnutri.filter(nutricion__edad__range=(1,15), nutricion__ninos__contains="ninos", nutricion__brazalete__id=5).count()
    #total de la tabla para niños
    total_v = normal_v + desnutrido_v + riesgo_v + nosabe_v
    #mandando los datos para el porcentaje del grafico niños
    p_normal_v = float(normal_v) / total_v if total_v !=0 else 0 
    p_desnutrido_v = float(desnutrido_v) / total_v if total_v !=0 else 0 
    p_riesgo_v = float(riesgo_v) / total_v if total_v !=0 else 0 
    p_nosabe_v = float(nosabe_v) / total_v if total_v !=0 else 0 
    # solo para niñas
    normal_m = gnutri.filter(nutricion__ninos__contains="ninas", nutricion__brazalete__id=1).count()
    desnutrido_m = gnutri.filter(nutricion__ninos__contains="ninas", nutricion__brazalete__id=3).count()
    riesgo_m = gnutri.filter(nutricion__ninos__contains="ninas", nutricion__brazalete__id=4).count()
    nosabe_m = gnutri.filter(nutricion__edad__range=(1,15), nutricion__ninos__contains="ninas", nutricion__brazalete__id=5).count()
    #total de la tabla para niñas
    total_m = normal_m + desnutrido_m + riesgo_m + nosabe_m 
    #mandando los datos para el porcentaje del grafico niños
    p_normal_m = float(normal_m) / total_m if total_m !=0 else 0 
    p_desnutrido_m = float(desnutrido_m) / total_m if total_m !=0 else 0 
    p_riesgo_m = float(riesgo_m) / total_m if total_m !=0 else 0 
    p_nosabe_m = float(nosabe_m) / total_m if total_m !=0 else 0     
    #mandar los datos al utils solo de niños y niñas
    lista1 = [p_normal_v,p_desnutrido_v,p_riesgo_v,p_nosabe_v]
    lista2 = [p_normal_m,p_desnutrido_m,p_riesgo_m,p_nosabe_m]
    legends1 = ['Normal','Desnutrido','Riesgo desnutricion','No sabe']
    legends2 = ['Normal','Desnutrido','Riesgo desnutricion','No sabe']
    mensa1 = "Grafico Nutrición Niños"
    mensa2 = "Grafico Nutrición Niñas"
    #los link para los grafos :)
    url = grafos.make_graph(lista1,legends1,mensa1,return_json=False)
    url1 = grafos.make_graph(lista2,legends2,mensa2,return_json=False)
    
    return render_to_response("encuesta/grafo_nutricion.html", locals())

@session_required
def grafo_disponibilidad(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado']
        gdispo = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        gdispo = Encuesta.objects.all()
        
    casos = gdispo.count()
    #conteo del maiz
    #TODO: sumas de toda la tabla disponibilidad
    total_maiz = 0
    total_frijol = 0
    total_sorgo =0
    prom_maiz = 0
    prom_frijol = 0
    prom_sorgo = 0
    for encuesta in gdispo:
        for disponibilidad in encuesta.disponibilidad.all():
            total_maiz= disponibilidad.maiz_disponible + total_maiz
            total_frijol = disponibilidad.frijol_disponible + total_frijol
            total_sorgo = disponibilidad.sorgo_disponible + total_sorgo
#    total_maiz=gdispo.aggregate(Sum('disponibilidad__maiz_disponible'))['disponibilidad__maiz_disponible__sum']
#    total_frijol=gdispo.aggregate(Sum('disponibilidad__frijol_disponible'))['disponibilidad__frijol_disponible__sum']
#    total_sorgo=gdispo.aggregate(Sum('disponibilidad__sorgo_disponible'))['disponibilidad__sorgo_disponible__sum'] 
    try:
        prom_maiz=float(total_maiz) / casos
    except:
        prom_maiz = 0
    try:
        prom_frijol=float(total_frijol) / casos
    except:
        prom_frijol = 0
    try:
        prom_sorgo=float(total_sorgo) / casos
    except:
        prom_sorgo = 0
    
#    sumatorias = [[prom_maiz],[prom_frijol],[prom_sorgo]]
#    sumatorias = gdispo.aggregate(maiz = Sum('disponibilidad__maiz_disponible'),
#                                           frijol = Sum('disponibilidad__frijol_disponible'),
#                                           sorgo = Sum('disponibilidad__sorgo_disponible')
#                                          )
    #grafo disponibilidad
#    data = [[float(valor)] for valor in sumatorias.values()]
    data = [[prom_maiz],[prom_frijol],[prom_sorgo]]
    legends = ['maiz', 'frijol', 'sorgo']        
#    legends = sumatorias.keys()
    message = "Quintales por familia"
    
    url_disp = grafos.make_graph(data, legends, message, multiline=True, 
                           return_json=False, type=GroupedVerticalBarChart)
    #con formula rara
    total_adulto = gdispo.aggregate(Sum('disponibilidad__adultos_casa'))['disponibilidad__adultos_casa__sum']
    total_ninos = gdispo.aggregate(Sum('disponibilidad__ninos_casa'))['disponibilidad__ninos_casa__sum']
    total_vacas = gdispo.aggregate(Sum('disponibilidad__vacas'))['disponibilidad__vacas__sum']
    total_cerdos = gdispo.aggregate(Sum('disponibilidad__cerdos'))['disponibilidad__cerdos__sum']
    total_gallinas = gdispo.aggregate(Sum('disponibilidad__gallinas'))['disponibilidad__gallinas__sum']
#    total_maiz = gdispo.aggregate(Sum('disponibilidad__maiz_disponible'))['disponibilidad__maiz_disponible__sum']
#    total_frijol = gdispo.aggregate(Sum('disponibilidad__frijol_disponible'))['disponibilidad__frijol_disponible__sum']
#    total_sorgo = gdispo.aggregate(Sum('disponibilidad__sorgo_disponible'))['disponibilidad__sorgo_disponible__sum']
#    prom_maiz = total_maiz/casos
#    prom_frijol = total_frijol/casos
#    prom_sorgo = total_sorgo/casos
    try:
        criterio1 = (float(total_maiz) * 100) / ((float(total_adulto) * 1) + (float(total_ninos) * 0.9))
    except:
        criterio1 = 0
    try:
        criterio2 = (float(total_frijol) * 100) / ((float(total_adulto) * 0.5) + (float(total_ninos) * 0.4))
    except:
        criterio2 = 0
    try:
        criterio3 = ((float(total_maiz) + float(total_sorgo)) * 100) / ((float(total_adulto) * 1) + (float(total_ninos) * 0.9) + (total_cerdos * 2.5)+(total_gallinas * 0.156))
    except:
        criterio3 = 0
    data = [[criterio1], [criterio2], [criterio3]]
    legends = ["Maiz-H", "Frijol-H", "Maiz+Sorgo-H+A"]
    message = "Disponibilidad en dias"

    url_disp_formula = grafos.make_graph(data, legends, message, multiline=True, 
                           return_json=False, type=GroupedVerticalBarChart)

    dicc = {'grafo_disp': url_disp, 'grafo_disp_formula': url_disp_formula, 
            'casos': casos}
    return direct_to_template(request, "encuesta/grafo_disponibilidad.html", dicc)

def __hoja_calculo__(request):
    fecha1=request.session['fecha_inicio']
    fecha2=request.session['fecha_final']
    if request.session['comunidad']:
        com = request.session['comunidad'].id
        if request.session['entrevistado'] !=None:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__id=com)
    elif request.session['municipio']:
        mun = request.session['municipio'].id
        if request.session['entrevistado'] !=None:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__id=mun)
    elif request.session['departamento']:
        dep = request.session['departamento'].id
        if request.session['entrevistado'] !=None:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=request.session['entrevistado'])
        else:
            encuestas = Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__comunidad__municipio__departamento__id=dep)
    elif request.session['entrevistado']:
        entre = request.session['entrevistado']
        encuestas= Encuesta.objects.filter(fecha__range=(fecha1,fecha2)).filter(entrevistado__nombre=entre)
    else:
        encuestas = Encuesta.objects.all()

    resultados = []

    #modelo de fila
    #[nombre, comunidad, primera producto, primera area sembrada, pri area cosechada, pri produccion pri perdida]
    for encuesta in encuestas:
        fila = []
        fila.append(encuesta.entrevistado.all()[0].nombre)
        fila.append(encuesta.entrevistado.all()[0].comunidad.nombre)
        #primera producto    primera area sembrada   primera area cosechada  primera produccion  razon
        productos = Producto.objects.all()
        #primera
        for producto in productos:
            fila.append(producto.nombre)
            try: 
                encuesta_producto = encuesta.primera.get(producto=producto)
                fila.append(encuesta_producto.area_sembrada)
                fila.append(encuesta_producto.area_cosechada)
                fila.append(encuesta_producto.produccion)
                fila.append(encuesta_producto.perdida.nombre)
            except:
                fila.append(0)
                fila.append(0)
                fila.append(0)
                fila.append('')

         #Postrera       
        for producto in productos:
           fila.append(producto.nombre)
           try: 
               encuesta_producto = encuesta.postrera.get(producto=producto)
               fila.append(encuesta_producto.area_sembrada)
               fila.append(encuesta_producto.area_cosechada)
               fila.append(encuesta_producto.produccion)
               fila.append(encuesta_producto.perdida.nombre)
           except:
               fila.append(0)
               fila.append(0)
               fila.append(0)
               fila.append('')
        try:
            fila.append(encuesta.disponibilidad.all()[0].adultos_casa)
            fila.append(encuesta.disponibilidad.all()[0].ninos_casa)
            fila.append(encuesta.disponibilidad.all()[0].vacas)
            fila.append(encuesta.disponibilidad.all()[0].cerdos)
            fila.append(encuesta.disponibilidad.all()[0].gallinas)
            fila.append(encuesta.disponibilidad.all()[0].maiz_disponible)
            fila.append(encuesta.disponibilidad.all()[0].frijol_disponible)
            fila.append(encuesta.disponibilidad.all()[0].sorgo_disponible)
            fila.append(encuesta.disponibilidad.all()[0].dinero)
        except:
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append(0)
            fila.append('')
            
             

        resultados.append(fila)
        
    dict = {'datos': resultados}
    return  dict

@session_required
def hoja_calculo_xls(request):
    dict = __hoja_calculo__(request)
    return write_xls('encuesta/hoja_calculo.html', dict, 'hoja_para_spss.xls')

def write_xls(template_src, context_dict, filename):
    response = render_to_response(template_src, context_dict)
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Charset']='UTF-8'
    return response
