# calculos/bono.py

from calculos.chapas import calcular_porcentaje, calcular_bap
from calculos.plywood import calcular_porcentaje_plywood, calcular_bap_plywood

# Función para calcular bonos para CHAPAS
def calcular_bono_chapas(chapas):
    porcentaje_chapas = calcular_porcentaje(chapas)
    bap_chapas = calcular_bap(chapas)[1]
    return porcentaje_chapas, bap_chapas

# Función para calcular bonos para PLYWOOD
def calcular_bono_plywood(plywood):
    porcentaje_plywood = calcular_porcentaje_plywood(plywood)
    bap_plywood = calcular_bap_plywood(plywood)[1]
    return porcentaje_plywood, bap_plywood
