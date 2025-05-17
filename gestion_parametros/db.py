import sqlite3
import os

# Ruta de la base de datos
RUTA_DB = "gestion_parametros/parametros.db"

def crear_tabla_bonos():
    """Crea la tabla 'bonos' si no existe."""
    with sqlite3.connect(RUTA_DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bonos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_bono TEXT NOT NULL,
            mes TEXT NOT NULL,
            valor_bono REAL NOT NULL,
            UNIQUE(nombre_bono, mes)
        )
        """)
        conexion.commit()

def crear_tabla_produccion_mensual():
    """Crea la tabla 'produccion_mensual' para almacenar los valores mensuales de producción."""
    with sqlite3.connect(RUTA_DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produccion_mensual (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mes TEXT NOT NULL,
                chapas REAL,
                porcentaje_chapas REAL,
                bap_chapas REAL,
                plywood REAL,
                porcentaje_plywood REAL,
                bap_plywood REAL,
                promedio_porcentaje REAL,
                promedio_bap REAL,
                UNIQUE(mes)
            )
        """)
        conexion.commit()

def inicializar_base_datos():
    """Inicializa la base de datos y crea las tablas necesarias."""
    db_creada = not os.path.exists(RUTA_DB)

    # Crear archivo vacío si no existe
    if db_creada:
        with sqlite3.connect(RUTA_DB):
            pass

    # Crear tablas vacías
    crear_tabla_bonos()
    crear_tabla_produccion_mensual()

    # Mensaje en consola solo si la DB fue recién creada
    if db_creada:
        print("✅ Base de datos iniciada correctamente.")

    return db_creada

def obtener_parametros():
    """Obtiene los parámetros de bonos de la base de datos."""
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_bono, mes, valor_bono FROM bonos")
        return cursor.fetchall()

def obtener_produccion_mensual():
    """Obtiene los valores de producción mensual de la base de datos."""
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, mes, chapas, porcentaje_chapas, bap_chapas, 
                   plywood, porcentaje_plywood, bap_plywood, 
                   promedio_porcentaje, promedio_bap
            FROM produccion_mensual
        """)
        return cursor.fetchall()

def insertar_parametro(nombre_bono, mes, valor_bono):
    """Inserta un nuevo parámetro de bono en la base de datos."""
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO bonos (nombre_bono, mes, valor_bono) VALUES (?, ?, ?)",
                           (nombre_bono, mes, valor_bono))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def actualizar_parametros_por_bono(nombre_bono, valores_por_mes):
    """Actualiza los valores de los parámetros de bonos por mes."""    
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        for mes, valor in valores_por_mes.items():
            cursor.execute("""
                INSERT INTO bonos (nombre_bono, mes, valor_bono)
                VALUES (?, ?, ?)
                ON CONFLICT(nombre_bono, mes) DO UPDATE SET valor_bono=excluded.valor_bono
            """, (nombre_bono, mes, valor))
        conn.commit()

def insertar_produccion_mensual(mes, chapas, porcentaje_chapas, bap_chapas,
                                 plywood, porcentaje_plywood, bap_plywood,
                                 promedio_porcentaje, promedio_bap):
    """Inserta los valores de producción mensual en la base de datos."""
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO produccion_mensual (
                    mes, chapas, porcentaje_chapas, bap_chapas,
                    plywood, porcentaje_plywood, bap_plywood,
                    promedio_porcentaje, promedio_bap
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (mes, chapas, porcentaje_chapas, bap_chapas,
                  plywood, porcentaje_plywood, bap_plywood,
                  promedio_porcentaje, promedio_bap))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def actualizar_produccion_mensual(mes, chapas, porcentaje_chapas, bap_chapas,
                                   plywood, porcentaje_plywood, bap_plywood,
                                   promedio_porcentaje, promedio_bap):
    """Actualiza los valores de producción mensual para un mes ya existente."""
    with sqlite3.connect(RUTA_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE produccion_mensual SET
                chapas = ?,
                porcentaje_chapas = ?,
                bap_chapas = ?,
                plywood = ?,
                porcentaje_plywood = ?,
                bap_plywood = ?,
                promedio_porcentaje = ?,
                promedio_bap = ?
            WHERE mes = ?
        """, (chapas, porcentaje_chapas, bap_chapas,
              plywood, porcentaje_plywood, bap_plywood,
              promedio_porcentaje, promedio_bap, mes))
        conn.commit()

def obtener_imm(mes):
    """Obtiene el valor del IMM para un mes específico desde la base de datos."""
    try:
        # Conectar a la base de datos
        with sqlite3.connect(RUTA_DB) as conn:
            cursor = conn.cursor()

            # Realizar la consulta para obtener el valor de IMM
            cursor.execute("SELECT valor_bono FROM bonos WHERE nombre_bono = 'IMM' AND mes = ?", (mes,))
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0]
            else:
                raise ValueError(f"No se encontró el valor de IMM para el mes {mes}.")
    
    except sqlite3.Error as e:
        print(f"Error al acceder a la base de datos: {e}")
        return None
