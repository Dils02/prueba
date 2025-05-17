def calcular_promedios(porcentaje_chapas, bap_chapas, porcentaje_plywood, bap_plywood):
    """
    Calcula los promedios de porcentaje y BAP.
    """
    promedio_porcentaje = (porcentaje_chapas + porcentaje_plywood) / 2
    promedio_bap = (bap_chapas + bap_plywood) / 2
    return promedio_porcentaje, promedio_bap
