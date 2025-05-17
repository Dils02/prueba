# Función para calcular BAP para PLYWOOD
def calcular_bap_plywood(plywood):
    if 3500 < plywood < 5500:
        bap = (plywood - 3100) * 14
        porcentaje = 14
    elif 5500 < plywood < 7000:
        bap = (plywood - 5500) * 16 + 33600 - 30000
        porcentaje = 16
    elif plywood >= 7000:
        bap = (plywood - 7000) * 28 + 57600 - 30000
        porcentaje = 28
    else:
        bap = 0
        porcentaje = 0
    return porcentaje, bap

# Función para calcular porcentaje para PLYWOOD
def calcular_porcentaje_plywood(plywood):
    BONO_PORCENTAJE_PLYWOOD = [
        {"desde": 0, "hasta": 3499, "bono": 0},
        {"desde": 3500, "hasta": 3999, "bono": 4},
        {"desde": 4000, "hasta": 4499, "bono": 9},
        {"desde": 4500, "hasta": 4699, "bono": 16},
        {"desde": 4700, "hasta": 4899, "bono": 18},
        {"desde": 4900, "hasta": 5099, "bono": 20},
        {"desde": 5100, "hasta": 5299, "bono": 22},
        {"desde": 5300, "hasta": 5599, "bono": 24},
        {"desde": 5600, "hasta": 6499, "bono": 25},
        {"desde": 6500, "hasta": 6999, "bono": 26},
        {"desde": 7000, "hasta": 7599, "bono": 27},
        {"desde": 7600, "hasta": 7799, "bono": 28},
        {"desde": 7800, "hasta": 7999, "bono": 29},
        {"desde": 8000, "hasta": 1000000000, "bono": 30}
    ]
    for rango in BONO_PORCENTAJE_PLYWOOD:
        if rango["desde"] <= plywood <= rango["hasta"]:
            return rango["bono"]
    return 0
