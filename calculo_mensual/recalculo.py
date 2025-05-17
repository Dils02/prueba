import pandas as pd
from .horas_extras import procesar_horas_extras  # Importamos la función que procesa las horas extras

MESES_VALIDOS = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

COLUMNA_CC = "Trabajo - Centro de Costo"
COLUMNA_TOTAL = "Total Costo Tulsa"

COLUMNAS_BONOS = [
    "Campos Personalizados de Empleado - Bono Responsabilidad",
    "Campos Personalizados de Empleado - BAP con descuento",
    "Campos Personalizados de Empleado - Gratificacion",
    "Campos Personalizados de Empleado - Asimilado Sindicato",
    "Campos Personalizados de Empleado - Bono Operacional",
    "Campos Personalizados de Empleado - Bono asistencia y movilidad",
    "Campos Personalizados de Empleado - Bono Asistencia",
    "Campos Personalizados de Empleado - Bono Turno",
    "Campos Personalizados de Empleado - Monto Asignación Colación",
    "Campos Personalizados de Empleado - Bono producción Planta",
    "Campos Personalizados de Empleado - Monto Asignación Movili",  # Corregido
    "Campos Personalizados de Empleado - Estudio y desempeño",
    "Campos Personalizados de Empleado - Bono Terreno",
    "Campos Personalizados de Empleado - Bono Tope Seguridad",
    "Campos Personalizados de Empleado - Bono producción Nuevo",
    "Campos Personalizados de Empleado - Bono Tope Supervisor"
]

def recalcular_excel_desde_workbook(workbook):
    hoja_resumen = workbook["Resumen Anual"]
    encabezados = [cell.value for cell in hoja_resumen[1]]

    if "Resumen" not in encabezados:
        raise Exception("❌ No se encontró la columna 'Resumen' en la hoja 'Resumen Anual'.")

    col_idx_cc = encabezados.index("Resumen")
    resumen_filas = {
        hoja_resumen.cell(row=i, column=col_idx_cc + 1).value: i
        for i in range(2, hoja_resumen.max_row + 1)
    }

    for mes in MESES_VALIDOS:
        if mes in workbook.sheetnames:
            ws = workbook[mes]
            columnas = [cell.value for cell in ws[1]]

            # Verificación de columnas necesarias
            if not all(col in columnas for col in COLUMNAS_BONOS + [COLUMNA_CC]):
                print(f"⚠️  No se encontraron todas las columnas necesarias en la hoja '{mes}', se omite.")
                continue

            df = pd.DataFrame(
                [[cell.value for cell in row] for row in ws.iter_rows(min_row=2)],
                columns=columnas
            ).fillna(0)

            # Conversión segura a numérico
            for col in COLUMNAS_BONOS:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", ".", regex=False),
                    errors='coerce'
                ).fillna(0)

            # Calcular Total Costo Tulsa
            df[COLUMNA_TOTAL] = df[COLUMNAS_BONOS].sum(axis=1)

            print(f"\n✅ Procesando hoja: {mes}")
            print("Bonos usados:", COLUMNAS_BONOS)
            print("Primeros valores calculados para Total Costo Tulsa:")
            print(df[COLUMNA_TOTAL].head())

            # Escribir columna en hoja mensual
            col_idx_total = columnas.index(COLUMNA_TOTAL) + 1 if COLUMNA_TOTAL in columnas else len(columnas) + 1
            if COLUMNA_TOTAL not in columnas:
                ws.cell(row=1, column=col_idx_total).value = COLUMNA_TOTAL

            for i, valor in enumerate(df[COLUMNA_TOTAL]):
                ws.cell(row=i + 2, column=col_idx_total).value = valor

            # Agrupación por centro de costo
            agrupado = df.groupby(COLUMNA_CC)[COLUMNA_TOTAL].sum()

            # Escribir en hoja "Resumen Anual"
            if mes not in encabezados:
                hoja_resumen.cell(row=1, column=len(encabezados) + 1).value = mes
                col_mes_idx = len(encabezados)
                encabezados.append(mes)
            else:
                col_mes_idx = encabezados.index(mes)

            for cc, total in agrupado.items():
                fila = resumen_filas.get(cc)
                if fila:
                    hoja_resumen.cell(row=fila, column=col_mes_idx + 1).value = total

    # Aquí llamamos a procesar horas extras, que actualizará las hojas mensuales con horas y montos HE
    print("\n🔄 Procesando horas extras...")
    workbook = procesar_horas_extras(workbook)
    print("✅ Horas extras procesadas y actualizadas.")

    return workbook
