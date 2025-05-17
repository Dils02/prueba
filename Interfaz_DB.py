import streamlit as st
from calculo_de_bono.interfaz import mostrar_interfaz_calculo_bono
from archivo_excel.visualizar_excel import mostrar_archivo_excel
from armado_de_tabla.interfaz import mostrar_interfaz_relleno_datos
from gestion_parametros.interfaz import mostrar_gestion_parametros
from gestion_parametros.db import inicializar_base_datos
from calculo_mensual.interfaz import mostrar_interfaz_calculo_mensual

# Función para aplicar los estilos del CSS
def aplicar_estilos():
    with open("assets/styles.css") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Inicializar la base de datos solo una vez
if "base_datos_inicializada" not in st.session_state:
    fue_creada = inicializar_base_datos()
    st.session_state["base_datos_inicializada"] = True

    if fue_creada:
        print("✅ Base de datos inicializada correctamente.")
        st.success("✅ Base de datos inicializada correctamente y parámetros verificados.")

# Aplicar estilos antes de mostrar la interfaz
aplicar_estilos()

# Título con colores personalizados
st.markdown(
    '<h1 class="titulo-tulsa"><span class="tul">TUL</span><span class="sa">SA</span></h1>',
    unsafe_allow_html=True
)

# Función para mostrar la interfaz principal (Inicio)
def mostrar_interfaz_principal():
    st.title("Bienvenido a su Página")
    st.write("Esta es la página principal donde puedes acceder a las diferentes funcionalidades del sistema.")
    st.write("Puedes navegar por las secciones desde el menú lateral.")

# Barra lateral para seleccionar la sección
page = st.sidebar.radio("Selecciona una sección", 
                        ("Inicio", "Cálculo de Bono", "Armado de Tabla", "Gestión de Parámetros", "Calculo Mensual"),
                        index=0)

# --- Sección de Inicio ---
if page == "Inicio":
    mostrar_interfaz_principal()

# --- Sección de Cálculo de Bono ---
elif page == "Cálculo de Bono":
    mostrar_interfaz_calculo_bono()

# --- Sección de Archivo Excel ---
elif page == "Calculo H.E":
    mostrar_archivo_excel()

# --- Sección de Relleno de Datos ---
elif page == "Armado de Tabla":
    mostrar_interfaz_relleno_datos()

# --- Sección de Gestión de Parámetros ---
elif page == "Gestión de Parámetros":
    mostrar_gestion_parametros()
    
# --- Seccion de Calculo Mensual ---
elif page == "Calculo Mensual":
    mostrar_interfaz_calculo_mensual()