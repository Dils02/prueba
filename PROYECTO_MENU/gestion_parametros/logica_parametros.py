import pandas as pd
from collections import defaultdict
from gestion_parametros.db import (
    obtener_parametros,
    obtener_produccion_mensual,
    insertar_parametro,
    actualizar_parametros_por_bono
)
from calculos.calculo_gratificacion import calcular_gratificacion

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def agregar_parametro(nombre_bono, mes, valor_str):
    nombre_bono_limpio = nombre_bono.strip()
    valor_limpio = valor_str.strip()

    if nombre_bono_limpio == "":
        return "warning", "⚠️ El nombre del bono no puede estar vacío."

    try:
        # Validación especial para IMM: debe ser un número entero, sin coma ni punto
        if nombre_bono_limpio.upper() == "IMM":
            if not valor_limpio.isdigit():
                return "error", "❌ El valor de 'IMM' debe ser un número entero sin puntos ni comas."
            valor_bono = int(valor_limpio)
        else:
            # Conversión normal para otros bonos
            valor_bono = float(valor_limpio.replace(',', '.').replace('%', ''))
            if '%' in valor_limpio:
                valor_bono /= 100

        exito = insertar_parametro(nombre_bono_limpio, mes, valor_bono)
        if not exito:
            return "error", "❌ Ya existe un bono con ese nombre y mes."

        if nombre_bono_limpio.upper() == "IPC":
            factor_ipc = round(1 + valor_bono / 100, 4)
            insertar_parametro("Factor IPC", mes, factor_ipc)

        if nombre_bono_limpio.upper() == "IMM":
            gratificacion = calcular_gratificacion(mes)
            insertar_parametro("Gratificación", mes, gratificacion)

        return "success", "✅ Parámetro agregado correctamente."
    except ValueError:
        return "error", "❌ Valor no válido. Ingresa un número como 0, 0.0 o 1,5."


def obtener_dataframe_parametros():
    datos = obtener_parametros()
    if not datos:
        return None, "❌ No se han encontrado parámetros en la base de datos."

    estructura = defaultdict(lambda: {mes: "" for mes in MESES})
    for _, nombre_bono, mes, valor in datos:
        estructura[nombre_bono][mes] = valor

    df_parametros = pd.DataFrame.from_dict(estructura, orient='index')
    df_parametros = df_parametros[MESES]
    return df_parametros, None


def limpiar_df_parametros(df_parametros):
    df_editable = df_parametros.copy().astype(str)
    for bono in df_parametros.index:
        for mes in df_parametros.columns:
            valor = df_parametros.loc[bono, mes]
            if isinstance(valor, (float, int)):
                bono_mayus = bono.strip().upper()
                if bono_mayus == "IPC":
                    df_editable.loc[bono, mes] = f"{valor:.1f}".replace('.', ',')
                elif bono_mayus == "FACTOR IPC":
                    df_editable.loc[bono, mes] = f"{valor:.3f}".replace('.', ',')
                else:
                    df_editable.loc[bono, mes] = f"{valor:.0f}".replace('.', ',')
            elif valor == "":
                df_editable.loc[bono, mes] = ""
    return df_editable


def guardar_cambios_parametros(df_original, df_editado):
    cambios_realizados = False
    errores = []

    for nombre_bono in df_editado.index:
        valores_mes = {}
        for mes in MESES:
            valor_original = df_original.loc[nombre_bono, mes]
            valor_nuevo = df_editado.loc[nombre_bono, mes]

            try:
                if valor_nuevo == "":
                    continue
                valor_limpio_nuevo = float(str(valor_nuevo).strip().replace(',', '.').replace('%', ''))
                if '%' in str(valor_nuevo):
                    valor_limpio_nuevo /= 100

                if valor_original == "":
                    valores_mes[mes] = valor_limpio_nuevo
                    cambios_realizados = True
                else:
                    valor_limpio_original = float(str(valor_original).strip().replace(',', '.').replace('%', ''))
                    if '%' in str(valor_original):
                        valor_limpio_original /= 100

                    if round(valor_limpio_nuevo, 6) != round(valor_limpio_original, 6):
                        valores_mes[mes] = valor_limpio_nuevo
                        cambios_realizados = True

                if nombre_bono.strip().upper() == "IPC":
                    factor_ipc = round(1 + valor_limpio_nuevo / 100, 4)
                    actualizar_parametros_por_bono("Factor IPC", {mes: factor_ipc})

                if nombre_bono.strip().upper() == "IMM":
                    gratificacion = calcular_gratificacion(mes)
                    actualizar_parametros_por_bono("Gratificación", {mes: gratificacion})

            except ValueError:
                errores.append(f"❌ Valor no válido para '{nombre_bono}' en {mes}.")

        if valores_mes:
            actualizar_parametros_por_bono(nombre_bono, valores_mes)

    return cambios_realizados, errores


def obtener_dataframe_produccion():
    datos_produccion = obtener_produccion_mensual()
    estructura = defaultdict(lambda: {mes: "" for mes in MESES})

    for _, mes, chapas, porcentaje_chapas, bap_chapas, plywood, porcentaje_plywood, bap_plywood, promedio_porcentaje, promedio_bap in datos_produccion:
        estructura[mes] = {
            "chapas": chapas,
            "porcentaje_chapas": porcentaje_chapas,
            "bap_chapas": bap_chapas,
            "plywood": plywood,
            "porcentaje_plywood": porcentaje_plywood,
            "bap_plywood": bap_plywood,
            "promedio_porcentaje": promedio_porcentaje,
            "promedio_bap": promedio_bap
        }

    df = pd.DataFrame.from_dict(estructura, orient='index')
    columnas = [
        "chapas", "porcentaje_chapas", "bap_chapas",
        "plywood", "porcentaje_plywood", "bap_plywood",
        "promedio_porcentaje", "promedio_bap"
    ]
    return df[columnas].T
