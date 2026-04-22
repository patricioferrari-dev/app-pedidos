import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema de Inventario", layout="wide")

# URL de tu hoja
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGA DE CATÁLOGO ---
@st.cache_data(ttl=600) # Guarda el catálogo 10 min en memoria para que sea rápido
def cargar_catalogo():
    try:
        # Lee la pestaña "Productos"
        return conn.read(spreadsheet=URL_HOJA, worksheet="Productos")
    except:
        return pd.DataFrame(columns=["Codigo", "Descripcion"])

df_catalogo = cargar_catalogo()

st.title("📦 Gestión de Materiales")

# --- FILA 1: FECHA Y TIPO ---
col_fecha, col_tipo = st.columns(2)
fecha_auto = datetime.now().strftime("%d/%m/%Y %H:%M")

with col_fecha:
    st.info(f"**Fecha actual:** {fecha_auto}")

with col_tipo:
    tipo_movimiento = st.selectbox(
        "Tipo de movimiento",
        ["Pedido de materiales", "Devolucion por fallas", "Otros"],
        label_visibility="collapsed"
    )

st.divider()

# --- FILA 2: CÓDIGO, DESCRIPCIÓN, CANTIDAD Y BOTÓN ---
# Usamos columnas para que quede todo en una línea "Abajo"
c1, c2, c3, c4 = st.columns([2, 4, 2, 2])

with c1:
    codigo_input = st.text_input("Código", placeholder="Ej: PER-01").upper().strip()

# Lógica de búsqueda automática
descripcion_auto = ""
if codigo_input:
    resultado = df_catalogo[df_catalogo["Codigo"] == codigo_input]
    if not resultado.empty:
        descripcion_auto = resultado.iloc[0]["Descripcion"]
    else:
        descripcion_auto = "⚠️ Código no encontrado"

with c2:
    # Mostramos la descripción (deshabilitada para que no se borre la lógica)
    st.text_input("Descripción", value=descripcion_auto, disabled=True)

with c3:
    cantidad_input = st.number_input("Cantidad", min_value=0, step=1)

with c4:
    st.write(" ") # Espacio para alinear con los inputs
    boton_cargar = st.button("🚀 Cargar", use_container_width=True)

# --- LÓGICA DE CARGA ---
if boton_cargar:
    if codigo_input and "⚠️" not in descripcion_auto and cantidad_input > 0:
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_auto,
            "Tipo": tipo_movimiento,
            "Codigo": codigo_input,
            "Descripcion": descripcion_auto,
            "Cantidad": cantidad_input
        }])
        
        try:
            df_existente = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
            df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
            conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)
            
            st.toast(f"¡{codigo_input} cargado con éxito!", icon="✅")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Verifica el código y que la cantidad sea mayor a 0.")

# --- HISTORIAL ---
st.divider()
st.subheader("📋 Últimos registros")
try:
    historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    st.dataframe(historial.iloc[::-1], use_container_width=True, hide_index=True)
except:
    st.write("Sin movimientos aún.")
