import pandas as pd
import streamlit as st
from io import BytesIO

def mostrar_archivo_excel():
    archivo_subido = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

    if archivo_subido is not None:
        st.session_state.archivo_subido = archivo_subido

    if archivo_subido is None and "archivo_subido" in st.session_state:
        del st.session_state.archivo_subido

    if "archivo_subido" in st.session_state:
        try:
            df_subido = pd.read_excel(st.session_state.archivo_subido)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo Excel: {e}")
            return

        # Validación de columnas requeridas
        columnas_requeridas = [
            "Empleado - Número de Documento",
            "Trabajo - Centro de Costo",
            "Trabajo - Cargo",
            "Campos Personalizados de Trabajo - Jornada",
            "Trabajo - Sueldo Base"
        ]
        if not all(col in df_subido.columns for col in columnas_requeridas):
            columnas_faltantes = [col for col in columnas_requeridas if col not in df_subido.columns]
            st.error(f"❌ El archivo no contiene las siguientes columnas necesarias: {', '.join(columnas_faltantes)}")
            return

        df_subido = df_subido.drop_duplicates(subset=["Empleado - Número de Documento"])

        df_subido_filtrado = df_subido[
            (df_subido["Trabajo - Centro de Costo"] >= 201) & 
            (df_subido["Trabajo - Centro de Costo"] <= 501)
        ]

        df_personas = df_subido_filtrado.groupby(
            ["Trabajo - Centro de Costo", "Trabajo - Cargo", "Campos Personalizados de Trabajo - Jornada"]
        )["Empleado - Número de Documento"].nunique().reset_index(name="#Personas")

        centro_costo_data = {}
        total_personas = 0
        datos_descarga = []

        for index, row in df_personas.iterrows():
            centro_costo = row['Trabajo - Centro de Costo']
            cargo = row['Trabajo - Cargo']
            turno = row['Campos Personalizados de Trabajo - Jornada']
            personas = row['#Personas']
            total_personas += personas

            centro_costo_data.setdefault(centro_costo, {}).setdefault(cargo, []).append({
                "Turno": turno,
                "Cantidad de personas": personas
            })

        for centro_costo, cargos in centro_costo_data.items():
            total_personas_centro = sum(
                sum(turno["Cantidad de personas"] for turno in turnos)
                for turnos in cargos.values()
            )

            with st.expander(f"📌 Centro de Costo: {centro_costo} (Total: {total_personas_centro} personas)"):
                for cargo, turnos in cargos.items():
                    st.markdown(f"### 🔧 Cargo: {cargo}")
                    total_personas_cargo = 0
                    sueldos_6x1 = []
                    sueldos_6x2 = []

                    for turno_info in turnos:
                        st.markdown(f"- ⏳ **Turno:** {turno_info['Turno']} - 👥 {turno_info['Cantidad de personas']} personas")
                        total_personas_cargo += turno_info['Cantidad de personas']

                        trabajadores_filtrados = df_subido_filtrado[
                            (df_subido_filtrado["Trabajo - Centro de Costo"] == centro_costo) &
                            (df_subido_filtrado["Trabajo - Cargo"] == cargo) &
                            (df_subido_filtrado["Campos Personalizados de Trabajo - Jornada"] == turno_info['Turno'])
                        ]

                        for sueldo in trabajadores_filtrados["Trabajo - Sueldo Base"].values:
                            if turno_info['Turno'] == "6x1":
                                sueldos_6x1.append(sueldo)
                            elif turno_info['Turno'] == "6x2":
                                sueldos_6x2.append(sueldo)

                    sueldo_promedio_6x1 = sum(sueldos_6x1) / len(sueldos_6x1) if sueldos_6x1 else None
                    sueldo_promedio_6x2 = sum(sueldos_6x2) / len(sueldos_6x2) if sueldos_6x2 else None

                    st.write(f"**Sueldo promedio para turno 6x1 en este cargo:** ${sueldo_promedio_6x1:,.2f}" if sueldo_promedio_6x1 else "No hay datos en Turno 6x1")
                    st.write(f"**Sueldo promedio para turno 6x2 en este cargo:** ${sueldo_promedio_6x2:,.2f}" if sueldo_promedio_6x2 else "No hay datos en Turno 6x2")
                    st.write(f"**Total de personas en este cargo:** {total_personas_cargo}")

                    datos_descarga.append([centro_costo, cargo, total_personas_cargo, sueldo_promedio_6x1, sueldo_promedio_6x2])

        st.write(f"## 👥 Total de personas en todos los centros de costo: {total_personas}")

        df_descarga = pd.DataFrame(datos_descarga, columns=[
            "Trabajo - Centro de Costo", "Trabajo - Cargo", "Total de Personas", 
            "Sueldo Promedio 6x1", "Sueldo Promedio 6x2"
        ])

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_descarga.to_excel(writer, sheet_name='Resumen', index=False)
        output.seek(0)

        st.download_button(
            label="📥 Descargar Archivo Excel",
            data=output,
            file_name="Resumen.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Por favor, sube un archivo Excel para continuar.")
