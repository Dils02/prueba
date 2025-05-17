# Función para calcular BAP para CHAPAS
def calcular_bap(chapas):
    if 4500 < chapas < 5500:
        bap = (chapas - 4500) * 12
        porcentaje = 12
    elif 5500 < chapas < 8700:
        bap = (chapas - 5500) * 17 + 12000 - 30000
        porcentaje = 17
    elif chapas >= 8700:
        bap = (chapas - 8700) * 32 + 66400 - 30000
        porcentaje = 32
    else:
        bap = 0
        porcentaje = 0
    return porcentaje, bap

# Función para calcular porcentaje para CHAPAS
def calcular_porcentaje(chapas):
    BONO_PORCENTAJE = [
        {"desde": 0, "hasta": 4499, "bono": 0},
        {"desde": 4500, "hasta": 4999, "bono": 4},
        {"desde": 5000, "hasta": 5499, "bono": 9},
        {"desde": 5500, "hasta": 5699, "bono": 16},
        {"desde": 5700, "hasta": 5899, "bono": 17},
        {"desde": 5900, "hasta": 6099, "bono": 18},
        {"desde": 6100, "hasta": 6299, "bono": 19},
        {"desde": 6300, "hasta": 6499, "bono": 20},
        {"desde": 6500, "hasta": 6699, "bono": 21},
        {"desde": 6700, "hasta": 6899, "bono": 22},
        {"desde": 6900, "hasta": 8499, "bono": 23},
        {"desde": 8500, "hasta": 8999, "bono": 24},
        {"desde": 9000, "hasta": 9299, "bono": 25},
        {"desde": 9300, "hasta": 9499, "bono": 26},
        {"desde": 9500, "hasta": 1000000000, "bono": 27}
    ]
    for rango in BONO_PORCENTAJE:
        if rango["desde"] <= chapas <= rango["hasta"]:
            return rango["bono"]
    return 0
