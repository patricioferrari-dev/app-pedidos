import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de pantalla ancha para que todo quepa en una fila
st.set_page_config(page_title="Control de Stock", layout="wide")

# URL de tu hoja
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CARGA DEL CATÁLOGO DE PRODUCTOS ---
@st.cache_data(ttl=60) # Se actualiza cada minuto por si agregas productos nuevos
def cargar_catalogo():
    try:
        # Lee la pestaña "Productos"
        df = conn.read(spreadsheet=URL_HOJA, worksheet="Productos")
        # Convertimos la columna Codigo a string para evitar problemas de comparación
        df["Codigo"] = df["Codigo"].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error cargando catálogo: {e}")
        return pd.DataFrame(columns=["Codigo", "Descripcion"])

df_catalogo = cargar_catalogo()

st.title("📦 Sistema de Carga de Materiales")

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
# Definimos anchos proporcionales para que se vea ordenado
c1, c2, c3, c4 = st.columns([2, 4, 1.5, 1.5])

with c1:
    # El usuario ingresa el código
    codigo_input = st.text_input("Código", placeholder="Ej: 30032").strip()

# Buscamos la descripción automáticamente
descripcion_detectada = ""
producto_valido = False

if codigo_input:
    # Buscamos en el catálogo
    match = df_catalogo[df_catalogo["Codigo"] == codigo_input]
    if not match.empty:
        descripcion_detectada = match.iloc[0]["Descripcion"]
        producto_valido = True
    else:
        descripcion_detectada = "❌ Código no registrado"

with c2:
    # Cuadro de descripción (solo lectura)
    st.text_input("Descripción", value=descripcion_detectada, disabled=True)

with c3:
    cantidad_input = st.number_input("Cantidad", min_value=1, step=1)

with c4:
    st.write(" ") # Espacio estético para alinear el botón
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
            # Leemos la Hoja1 (donde van los pedidos)
            df_historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
            df_final = pd.concat([df_historial, nuevo_registro], ignore_index=True)
            
            # Guardamos
            conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)
            
            st.toast(f"¡{descripcion_detectada} cargado!", icon="✅")
            st.balloons()
            # Forzamos recarga para ver el historial limpio
            st.rerun()
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        if not producto_valido:
            st.warning("⚠️ No puedes cargar un código que no existe en el catálogo.")
        else:
            st.warning("⚠️ La cantidad debe ser al menos 1.")

# --- TABLA DE ÚLTIMOS MOVIMIENTOS ---
st.subheader("📋 Historial de Cargas (Hoja1)")
try:
    historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    if not historial.empty:
        # Mostramos los últimos 10 movimientos arriba
        st.dataframe(historial.iloc[::-1].head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos registrados aún.")
except:
    st.info("La Hoja1 está lista para recibir datos.")
