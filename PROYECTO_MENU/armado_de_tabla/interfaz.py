# Relleno_de_Datos/interfaz.py

import streamlit as st
import os
import tempfile

# Importación necesaria
from armado_de_tabla.procesar_excel import procesar_archivo_excel

def mostrar_interfaz_relleno_datos():
    """Función para visualizar la interfaz de la sección 'Relleno de Datos' en Streamlit."""
    st.title("📂 Armado de tabla Excel")

    # 📤 Subida de Archivo
    archivo_subido = st.file_uploader(
        "**Cargar archivo Excel**", type=["xlsx"], help="Selecciona un archivo Excel (.xlsx)")

    if archivo_subido:
        # Guardar el archivo en un temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            ruta_temporal = temp_file.name
            temp_file.write(archivo_subido.getbuffer())

        st.success("✅ **Archivo cargado correctamente**")

        # 🔄 Procesamiento del Archivo
        if st.button("🔄 Procesar Archivo"):
            with st.spinner("⏳ Procesando..."):
                try:
                    # Solo estructura las hojas: Datos, Horas Extras y hojas mensuales
                    ruta_procesada = procesar_archivo_excel(ruta_temporal)

                    st.success("✅ **Archivo procesado correctamente**")

                    # 📥 Descargar Archivo Procesado con nombre personalizado
                    # Cambiar el nombre de descarga a "Armado_PPTO.xlsx"
                    with open(ruta_procesada, "rb") as archivo:
                        st.download_button(
                            label="📥 Descargar Archivo Procesado",
                            data=archivo,
                            file_name="Armado_PPTO.xlsx",  # Cambiar el nombre del archivo descargado
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"⚠️ **Error al procesar el archivo:** {e}")
