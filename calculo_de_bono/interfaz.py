import streamlit as st
from calculos.bono import calcular_bono_chapas, calcular_bono_plywood
from gestion_parametros.db import insertar_produccion_mensual, actualizar_produccion_mensual, obtener_produccion_mensual
import sqlite3

# Verifica si la tabla existe
def tabla_produccion_existe():
    try:
        conn = sqlite3.connect("gestion_parametros/parametros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produccion_mensual'")
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None
    except sqlite3.Error:
        return False

def mostrar_interfaz_calculo_bono():
    # Iniciar variables en session_state
    variables = [
        'porcentaje_chapas', 'bap_chapas', 'porcentaje_plywood', 'bap_plywood',
        'chapas', 'plywood', 'promedio_porcentaje', 'promedio_bap',
        'bono_chapas_listo', 'bono_plywood_listo'
    ]
    for var in variables:
        if var not in st.session_state:
            st.session_state[var] = 0 if 'porcentaje' in var or 'bap' in var or 'chapas' in var or 'plywood' in var else False

    # Selección del mes
    mes = st.selectbox("**Selecciona el mes**", [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ])

    st.write("---")
    col1, col2 = st.columns(2)

    datos_existentes = obtener_produccion_mensual() if tabla_produccion_existe() else []

    with col1:
        st.markdown("### Bono para CHAPAS")
        chapas_input = st.text_input("Ingrese CHAPAS producidas:", value="0")
        if st.button("Calcular Bono para CHAPAS"):
            chapas = int(chapas_input) if chapas_input.isdigit() else 0
            porcentaje, bap = calcular_bono_chapas(chapas)
            st.session_state.chapas = chapas
            st.session_state.porcentaje_chapas = int(porcentaje)
            st.session_state.bap_chapas = round(bap)
            st.session_state.bono_chapas_listo = True
            st.success(f"CHAPAS: {porcentaje:.0f}% - BAP: ${bap:,.0f}")

    with col2:
        st.markdown("### Bono para PLYWOOD")
        plywood_input = st.text_input("Ingrese PLYWOOD producido:", value="0")
        if st.button("Calcular Bono para PLYWOOD"):
            plywood = int(plywood_input) if plywood_input.isdigit() else 0
            porcentaje, bap = calcular_bono_plywood(plywood)
            st.session_state.plywood = plywood
            st.session_state.porcentaje_plywood = int(porcentaje)
            st.session_state.bap_plywood = round(bap)
            st.session_state.bono_plywood_listo = True
            st.success(f"PLYWOOD: {porcentaje:.0f}% - BAP: ${bap:,.0f}")

    st.write("---")

    if st.session_state.bono_chapas_listo and st.session_state.bono_plywood_listo:
        # Calcular promedio y guardar
        st.session_state.promedio_porcentaje = (
            st.session_state.porcentaje_chapas + st.session_state.porcentaje_plywood
        ) / 2
        st.session_state.promedio_bap = (
            st.session_state.bap_chapas + st.session_state.bap_plywood
        ) / 2

        if any(item[1] == mes for item in datos_existentes):
            actualizar_produccion_mensual(
                mes,
                st.session_state.chapas,
                st.session_state.porcentaje_chapas,
                st.session_state.bap_chapas,
                st.session_state.plywood,
                st.session_state.porcentaje_plywood,
                st.session_state.bap_plywood,
                st.session_state.promedio_porcentaje,
                st.session_state.promedio_bap
            )
        else:
            insertar_produccion_mensual(
                mes,
                st.session_state.chapas,
                st.session_state.porcentaje_chapas,
                st.session_state.bap_chapas,
                st.session_state.plywood,
                st.session_state.porcentaje_plywood,
                st.session_state.bap_plywood,
                st.session_state.promedio_porcentaje,
                st.session_state.promedio_bap
            )

        st.success(f"✅ Producción registrada para {mes}. Promedio: {st.session_state.promedio_porcentaje:.0f}% - BAP: ${st.session_state.promedio_bap:,.0f}")

        # Resetear los flags
        st.session_state.bono_chapas_listo = False
        st.session_state.bono_plywood_listo = False
