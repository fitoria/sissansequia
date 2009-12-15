from models import MES_CHOICES

def convertir_mes(mes):
    return MES_CHOICES[mes-1][1]
