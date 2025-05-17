import streamlit as st
from gestion_parametros.logica_parametros import (
    MESES, agregar_parametro,
    obtener_dataframe_parametros,
    limpiar_df_parametros,
    guardar_cambios_parametros,
    obtener_dataframe_produccion
)

def mostrar_gestion_parametros():
    st.markdown("<h1 class='titulo'>Gestión de Parámetros</h1>", unsafe_allow_html=True)

    with st.expander("📌 Agregar Nuevo Parámetro", expanded=False):
        nombre_bono = st.text_input("🔹 Nombre del Bono")
        mes = st.selectbox("🔹 Mes", MESES)
        valor_str = st.text_input("🔹 Valor del Bono (ej: $100.000, 1,7 o 5,0%)")

        if st.button("➕ Agregar", use_container_width=True):
            estado, mensaje = agregar_parametro(nombre_bono, mes, valor_str)
            getattr(st, estado)(mensaje)

    st.markdown("---")

    with st.expander("📄 Parámetros Existentes", expanded=False):
        df_parametros, mensaje = obtener_dataframe_parametros()
        if mensaje:
            st.warning(mensaje)
        else:
            df_editable = limpiar_df_parametros(df_parametros)
            st.markdown("### ✏️ Editar Valores de Parametros por Mes")
            edited_df = st.data_editor(
                df_editable,
                use_container_width=True,
                key="tabla_dinamica_bonos",
                num_rows="dynamic"
            )

            if st.button("💾 Guardar Cambios", use_container_width=True):
                cambios, errores = guardar_cambios_parametros(df_parametros, edited_df)
                if errores:
                    for e in errores:
                        st.error(e)
                elif cambios:
                    st.success("✅ Cambios guardados correctamente.")
                    st.rerun()
                else:
                    st.info("ℹ️ No se detectaron cambios.")

    st.markdown("---")

    with st.expander("📄 Producción Mensual", expanded=False):
        df_produccion = obtener_dataframe_produccion()
        st.dataframe(df_produccion, use_container_width=True)
