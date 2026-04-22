import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Stock Horizontal", layout="centered")

# --- 1. TU CATÁLOGO ---
CATALOGO = {
    "30032": "Tarugo de 8mm para ladrillo hueco",
    "012009U": "Fuentes 12V-1,5A para decos UHF Inspur Model STB STB-6755TI",
    "13008": "CONTROL REMOTO PARA DECO SAGECOM DCWMI303. CON BOTONES YT + NETFLIX",
    "13012": "CONTROL REMOTO POR VOZ PARA DECO SAGEMCOM V2",
    "13013": "CONTROL REMOTO POR VOZ V3 PARA DECO SAGEMCOM 362 - VSB3930",
}

URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 Control de Inventario (Carga Horizontal)")

# --- INTERFAZ VERTICAL ---
# 1. Tipo de movimiento (será parte del encabezado)
tipo_movimiento = st.selectbox(
    "Seleccione el tipo de movimiento:",
    ["Ingreso", "Devolucion por falla", "Devolucion"]
)

# 2. Código
codigo_input = st.text_input("Ingrese el Código del Artículo:").strip()

descripcion_detectada = ""
producto_valido = False

if codigo_input:
    if codigo_input in CATALOGO:
        descripcion_detectada = CATALOGO[codigo_input]
        producto_valido = True
    else:
        descripcion_detectada = "❌ Código no encontrado"

# 3. Mostrar Artículo
st.text_input("Artículo:", value=descripcion_detectada, disabled=True)

# 4. Cantidad
cantidad_input = st.number_input("Cantidad:", min_value=1, step=1)

# 5. Botón
boton_cargar = st.button("💾 Registrar Movimiento", use_container_width=True)

# --- LÓGICA DE ACTUALIZACIÓN HORIZONTAL ---
if boton_cargar:
    if producto_valido and cantidad_input > 0:
        try:
            # Leer la hoja completa
            df = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
            
            # Limpiar columna Código para comparar (quitar espacios, etc)
            df['Codigo'] = df['Codigo'].astype(str).str.strip()
            
            if codigo_input in df['Codigo'].values:
                # CREAR NOMBRE DE COLUMNA: "Tipo - Fecha" (Ej: "Ingreso 11/06/2025")
                fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                nueva_columna = f"{tipo_movimiento} {fecha_hoy}"
                
                # Si la columna no existe en el Excel, la creamos vacía
                if nueva_columna not in df.columns:
                    df[nueva_columna] = None
                
                # Lógica de signo: Si es devolución por falla, restamos
                valor_final = cantidad_input
                if tipo_movimiento == "Devolucion por falla":
                    valor_final = cantidad_input * -1
                
                # Buscamos la fila exacta y asignamos el valor
                # Nota: Si ya existe un valor en esa columna para ese día, lo suma
                fila_idx = df[df['Codigo'] == codigo_input].index[0]
                valor_actual = df.at[fila_idx, nueva_columna]
                
                if pd.isna(valor_actual):
                    df.at[fila_idx, nueva_columna] = valor_final
                else:
                    df.at[fila_idx, nueva_columna] = valor_actual + valor_final
                
                # Guardar en Google Sheets
                conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df)
                
                st.success(f"✅ Registrado: {nueva_columna} para {codigo_input}")
                st.balloons()
                st.rerun()
            else:
                st.error("El código no existe en la columna 'Codigo' de tu Excel.")
                
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Complete los datos correctamente.")

# --- VISTA PREVIA ---
st.divider()
st.subheader("📋 Vista de la Planilla")
try:
    df_vista = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    st.dataframe(df_vista, use_container_width=True, hide_index=True)
except:
    st.info("Sin datos para mostrar.")
