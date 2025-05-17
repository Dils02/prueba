import pandas as pd

def calcular_valor_he(sueldo_base, jornada, factor_base, multiplicador):
    """
    Calcula el valor unitario de una hora extra.
    Fórmula general:
    S.B. x ((((1/30)*28)/factor_base)*multiplicador)
    """
    return sueldo_base * (((1/30)*28)/factor_base) * multiplicador

def procesar_horas_extras(wb):
    meses_validos = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    if "Horas Extras" not in wb.sheetnames:
        raise ValueError("No se encontró la hoja 'Horas Extras' en el libro.")

    ws_he = wb["Horas Extras"]

    # Leer encabezado multinivel (2 filas) manualmente:
    encabezado_1 = [cell.value for cell in ws_he[1]]  # fila 1 = meses o columna fija
    encabezado_2 = [cell.value for cell in ws_he[2]]  # fila 2 = subtipo o nombre columna fija

    # Construir nombres combinados para columnas, ejemplo: "Enero HE 80% 6x2"
    columnas_combinadas = []
    for top, sub in zip(encabezado_1, encabezado_2):
        if top is None and sub is None:
            columnas_combinadas.append(None)
        elif top is None:
            columnas_combinadas.append(str(sub))
        elif sub is None or top == sub:
            columnas_combinadas.append(str(top))
        else:
            columnas_combinadas.append(f"{top} {sub}")

    # Leer datos desde fila 3 en adelante
    data = [[cell.value for cell in row] for row in ws_he.iter_rows(min_row=3)]

    # Crear DataFrame con columnas combinadas
    df_he = pd.DataFrame(data, columns=columnas_combinadas)

    # Columnas clave para buscar datos fijos
    columnas_claves = [
        "Empleado - Número de Documento",
        "Trabajo - Sueldo Base",
        "Campos Personalizados de Trabajo - Jornada"
    ]

    # Validar que existan las columnas clave
    for c in columnas_claves:
        if c not in df_he.columns:
            raise ValueError(f"No se encontró la columna clave '{c}' en 'Horas Extras'")

    # Mapa para horas extras (factor_base, multiplicador, nombre tipo HE)
    mapa_he = {
        "HE 55% 6x1":  (176, 1.55, "HE 55% 6x1"),
        "HE 100% 6x1": (176, 2.00, "HE 100% 6x1"),
        "HE 150% 6x1": (176, 2.50, "HE 150% 6x1"),
        "HE 50% 6x2":  (157.52, 1.50, "HE 50% 6x2"),
        "HE 80% 6x2":  (157.52, 1.80, "HE 80% 6x2"),
        "HE 100% 6x2": (157.52, 2.00, "HE 100% 6x2"),
        "HE 120% 6x2": (157.52, 2.20, "HE 120% 6x2"),
        "HE 50% 5x2":  (174, 1.50, "HE 50% 5x2"),  # ADM = 5x2
    }

    for mes in meses_validos:
        if mes not in wb.sheetnames:
            continue

        ws_mes = wb[mes]

        # Leer encabezados de la hoja mensual (fila 1)
        encabezados = [cell.value for cell in ws_mes[1]]

        # Crear diccionario columna -> índice (1-based para openpyxl)
        col_idx = {col: idx+1 for idx, col in enumerate(encabezados)}

        # Leer columna "Empleado - Número de Documento" para buscar fila por Rut
        ruts = [ws_mes.cell(row=row, column=col_idx["Empleado - Número de Documento"]).value
                for row in range(2, ws_mes.max_row + 1)]

        for idx_he, fila_he in df_he.iterrows():
            rut_he = fila_he["Empleado - Número de Documento"]
            sueldo_base = fila_he["Trabajo - Sueldo Base"]
            jornada = fila_he["Campos Personalizados de Trabajo - Jornada"]

            if rut_he not in ruts:
                continue

            fila_excel = ruts.index(rut_he) + 2  # +2 porque fila 2 es primer dato

            for tipo_he, (factor_base, multiplicador, _) in mapa_he.items():
                columna_he = f"{mes} {tipo_he}"
                if columna_he not in df_he.columns:
                    continue

                cantidad_horas = fila_he[columna_he]
                if cantidad_horas is None or cantidad_horas == 0:
                    continue

                valor_unitario = calcular_valor_he(sueldo_base, jornada, factor_base, multiplicador)
                monto_he = valor_unitario * cantidad_horas

                col_horas_mes = tipo_he
                col_monto_mes = f"Monto {tipo_he}"

                if col_horas_mes in col_idx:
                    ws_mes.cell(row=fila_excel, column=col_idx[col_horas_mes], value=cantidad_horas)
                else:
                    print(f"Columna '{col_horas_mes}' no encontrada en hoja '{mes}'")

                if col_monto_mes in col_idx:
                    ws_mes.cell(row=fila_excel, column=col_idx[col_monto_mes], value=monto_he)
                else:
                    print(f"Columna '{col_monto_mes}' no encontrada en hoja '{mes}'")

    return wb
