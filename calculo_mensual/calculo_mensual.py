import pandas as pd
import sqlite3
import json
import os
from calculo_mensual.rellenar_resumen_anual import rellenar_resumen_anual_totales

# Ruta a la base de datos de parámetros y al archivo de mapeo de bonos
DB_PATH = 'gestion_parametros/parametros.db'
MAPEO_BONOS_PATH = os.path.join('calculo_mensual', 'mapeo_bonos.json')

def leer_parametros_del_mes(mes: str) -> dict:
    """Lee los valores de bonos desde la base de datos para un mes dado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre_bono, valor_bono FROM bonos WHERE mes = ?", 
        (mes,)
    )
    datos = cursor.fetchall()
    conn.close()
    return {nombre: valor for nombre, valor in datos}

def cargar_mapeo_bonos() -> dict:
    """Carga el archivo JSON que mapea bonos a columnas del Excel."""
    with open(MAPEO_BONOS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def asignar_bonos(df: pd.DataFrame, mes: str, parametros: dict, mapeo: dict) -> pd.DataFrame:
    """Asigna valores de bonos en el DataFrame. Si es 'sí', aplica el valor; en caso contrario (incluyendo vacío o 'no'), pone 0."""
    df = df.copy()

    for bono, columna_datos in mapeo.items():
        if columna_datos not in df.columns:
            continue

        valor_bono = parametros.get(bono)

        if valor_bono is not None:
            try:
                valor_bono = int(round(float(valor_bono)))  # 🔧 Fuerza entero limpio
            except Exception as e:
                print(f"⚠️ Valor inválido para el bono '{bono}': {valor_bono} ({e})")
                valor_bono = 0

            def transformar_valor(x):
                if isinstance(x, str) and x.strip().lower() in ["sí", "si", "sì"]:
                    return valor_bono
                else:
                    return 0

            df[columna_datos] = df[columna_datos].fillna('').apply(transformar_valor)

    return df



def reajustar_sueldo_base(df: pd.DataFrame, parametros: dict) -> pd.DataFrame:
    """Aplica el reajuste del sueldo base usando el Factor IPC del mes, si está disponible."""
    df = df.copy()
    columna_sueldo = "Trabajo - Sueldo Base"
    factor_ipc = parametros.get("Factor IPC")

    if columna_sueldo in df.columns and factor_ipc is not None:
        try:
            df[columna_sueldo] = df[columna_sueldo].apply(
                lambda x: round(float(x) * float(factor_ipc)) if pd.notnull(x) else x
            )
        except Exception as e:
            print(f"⚠️ Error al aplicar el reajuste de sueldo base: {e}")

    return df

def procesar_calculo_mensual(df: pd.DataFrame, mes: str) -> pd.DataFrame:
    """Función principal que procesa el cálculo mensual: reajuste + asignación de bonos."""
    parametros = leer_parametros_del_mes(mes)
    mapeo = cargar_mapeo_bonos()

    df = reajustar_sueldo_base(df, parametros)
    df = asignar_bonos(df, mes, parametros, mapeo)

    # Lista de columnas a sumar para calcular el Total Costo Tulsa
    columnas_bonos = [
        "Campos Personalizados de Empleado - BAP con descuento",
        "Campos Personalizados de Empleado - Gratificacion",
        "Campos Personalizados de Empleado - Asimilado Sindicato",
        "Campos Personalizados de Empleado - Bono Responsabilidad",
        "Campos Personalizados de Empleado - Bono Operacional",
        "Campos Personalizados de Empleado - Bono asistencia y movilidad",
        "Campos Personalizados de Empleado - Bono Asistencia",
        "Campos Personalizados de Empleado - Bono Turno",
        "Campos Personalizados de Empleado - Monto Asignación Colación",
        "Campos Personalizados de Empleado - Monto Asignación Movili",
        "Campos Personalizados de Empleado - Estudio y desempeño",
        "Campos Personalizados de Empleado - Bono Terreno",
        "Campos Personalizados de Empleado - Bono Tope Seguridad",
        "Campos Personalizados de Empleado - Bono producción Planta",
        "Campos Personalizados de Empleado - Bono producción Nuevo",
        "Campos Personalizados de Empleado - Bono Tope Supervisor"
    ]

    # Convertir las columnas a numérico si existen y sumar por fila
    columnas_existentes = [col for col in columnas_bonos if col in df.columns]
    df["Total Costo Tulsa"] = df[columnas_existentes].apply(
        lambda fila: pd.to_numeric(fila, errors='coerce').sum(), axis=1
    )

    return df

def procesar_archivo_excel(ruta_archivo_excel, mes: str):
    """Lee el archivo Excel, procesa el mes seleccionado y aplica reajuste + bonos."""
    try:
        # Cargar la hoja correspondiente al mes
        df_mensual = pd.read_excel(ruta_archivo_excel, sheet_name=mes)

        # Procesar el DataFrame (reajuste sueldo base + asignación de bonos)
        df_mensual_procesado = procesar_calculo_mensual(df_mensual, mes)

        # Guardar el archivo modificado
        with pd.ExcelWriter(ruta_archivo_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_mensual_procesado.to_excel(writer, sheet_name=mes, index=False)

        # Actualizar hoja Resumen Anual
        rellenar_resumen_anual_totales(ruta_archivo_excel, mes)

        print(f"✅ El archivo {ruta_archivo_excel} ha sido procesado correctamente.")

    except Exception as e:
        print(f"⚠️ Ocurrió un error al procesar el archivo: {e}")

