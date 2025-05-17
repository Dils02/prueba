from gestion_parametros.db import obtener_imm

def calcular_gratificacion(mes):
    """Calcula la gratificación en base al IMM del mes."""
    imm = obtener_imm(mes)

    if imm is not None:
        gratificacion = round((imm * 4.75) / 12, 3)
        return gratificacion
    else:
        return None
