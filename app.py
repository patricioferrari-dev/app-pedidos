import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Stock Directo", layout="wide")

# --- 1. TU CATÁLOGO DE PRODUCTOS (Edita esto cuando quieras) ---
# Formato: "CODIGO": "DESCRIPCIÓN"
CATALOGO = {
    "30032": "Cable",
    "40050": "Tornillo 2 pulgadas",
    "50010": "Pintura sintética blanca",
    "12345": "Herramienta de prueba",
    # Puedes seguir agregando aquí abajo...
}

# URL de tu hoja (Hoja1 para guardar)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📦 Sistema de Carga Directa")

# --- FILA SUPERIOR: FECHA Y TIPO ---
fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
col_f1, col_f2 = st.columns([1, 1])

with col_f1:
    st.write(f"📅 **Fecha Automática:** {fecha_hoy}")

with col_f2:
    tipo_movimiento = st.selectbox(
        "Tipo de movimiento",
        ["Pedido de materiales", "Devolucion por fallas", "Otros"],
        label_visibility="collapsed"
    )

st.markdown("---")

# --- FILA DE CARGA: CODIGO, DESCRIPCION, CANTIDAD Y BOTON ---
c1, c2, c3, c4 = st.columns([2, 4, 1.5, 1.5])

with c1:
    codigo_input = st.text_input("Código", placeholder="Escribe el código aquí...").strip()

# Verificamos si el código existe en nuestro diccionario de arriba
descripcion_detectada = ""
producto_valido = False

if codigo_input:
    if codigo_input in CATALOGO:
        descripcion_detectada = CATALOGO[codigo_input]
        producto_valido = True
    else:
        descripcion_detectada = "❌ Código no encontrado en sistema"

with c2:
    # Mostramos la descripción fija del diccionario
    st.text_input("Descripción", value=descripcion_detectada, disabled=True)

with c3:
    cantidad_input = st.number_input("Cantidad", min_value=0, step=1)

with c4:
    st.write(" ") 
    boton_cargar = st.button("📥 Cargar", use_container_width=True)

# --- PROCESO DE GUARDADO ---
if boton_cargar:
    if producto_valido and cantidad_input > 0:
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Tipo": tipo_movimiento,
            "Codigo": codigo_input,
            "Descripcion": descripcion_detectada,
            "Cantidad": cantidad_input
        }])
        
        try:
            # Solo leemos y escribimos en la Hoja1
            df_historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
            df_final = pd.concat([df_historial, nuevo_registro], ignore_index=True)
            
            conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)
            
            st.toast(f"✅ Cargado: {descripcion_detectada}", icon="🚀")
            st.balloons()
            st.rerun() # Refresca para limpiar campos
        except Exception as e:
            st.error(f"Error al conectar con Google Sheets: {e}")
    else:
        if not producto_valido and codigo_input:
            st.warning("⚠️ Debes usar un código válido del catálogo.")
        elif cantidad_input <= 0:
            st.warning("⚠️ Ingresa una cantidad mayor a 0.")

# --- TABLA DE ÚLTIMOS MOVIMIENTOS ---
st.subheader("📋 Registro de Movimientos (Hoja1)")
try:
    historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    if not historial.empty:
        st.dataframe(historial.iloc[::-1].head(10), use_container_width=True, hide_index=True)
except:
    st.info("Listo para recibir el primer registro.")
