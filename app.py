import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Carga de Remitos", layout="centered")

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

# --- INICIALIZAR CARRITO (Session State) ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

st.title("📑 Carga de Remito Multi-Producto")

# --- SECCIÓN 1: CONFIGURACIÓN DEL MOVIMIENTO ---
st.subheader("1. Configuración del Movimiento")
tipo_movimiento = st.selectbox(
    "Seleccione el tipo de movimiento para todo el remito:",
    ["Ingreso", "Devolucion por falla", "Devolucion"]
)

st.divider()

# --- SECCIÓN 2: AGREGAR PRODUCTOS AL LISTADO ---
st.subheader("2. Agregar Productos")
c1, c2 = st.columns([1, 1])

with c1:
    codigo_input = st.text_input("Código:", key="input_cod").strip()
with c2:
    cantidad_input = st.number_input("Cantidad:", min_value=1, step=1, key="input_cant")

descripcion_detectada = ""
if codigo_input:
    descripcion_detectada = CATALOGO.get(codigo_input, "❌ Código no encontrado")
    st.caption(f"**Artículo:** {descripcion_detectada}")

if st.button("➕ Agregar a la lista"):
    if codigo_input in CATALOGO and cantidad_input > 0:
        # Guardamos en la lista temporal
        st.session_state.carrito.append({
            "Codigo": codigo_input,
            "Articulo": CATALOGO[codigo_input],
            "Cantidad": cantidad_input
        })
        st.toast(f"Agregado: {codigo_input}")
    else:
        st.error("Código no válido o cantidad en cero.")

# --- SECCIÓN 3: VISTA PREVIA Y CARGA FINAL ---
if st.session_state.carrito:
    st.divider()
    st.subheader("📋 Productos en este Remito")
    
    # Mostrar tabla del carrito
    df_carrito = pd.DataFrame(st.session_state.carrito)
    st.table(df_carrito)

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🗑️ Borrar Lista", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

    with col_btn2:
        if st.button("🚀 CARGAR REMITO FINAL", type="primary", use_container_width=True):
            try:
                # 1. Leer Excel
                df_excel = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                df_excel['Codigo'] = df_excel['Codigo'].astype(str).str.strip()
                
                # 2. Definir columna (Tipo + Fecha)
                fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                nueva_columna = f"{tipo_movimiento} {fecha_hoy}"
                
                if nueva_columna not in df_excel.columns:
                    df_excel[nueva_columna] = 0.0

                # 3. Procesar cada item del carrito
                for item in st.session_state.carrito:
                    cod = item["Codigo"]
                    cant = item["Cantidad"]
                    
                    if tipo_movimiento == "Devolucion por falla":
                        cant = cant * -1
                    
                    if cod in df_excel['Codigo'].values:
                        idx = df_excel[df_excel['Codigo'] == cod].index[0]
                        # Sumar a lo que ya hay en esa celda
                        val_actual = df_excel.at[idx, nueva_columna]
                        if pd.isna(val_actual): val_actual = 0
                        df_excel.at[idx, nueva_columna] = val_actual + cant
                
                # 4. Subir todo de una vez
                conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_excel)
                
                st.success(f"✅ ¡Remito cargado exitosamente en la columna {nueva_columna}!")
                st.session_state.carrito = [] # Limpiar carrito
                st.balloons()
                # st.rerun() # Opcional: refrescar para limpiar pantalla
                
            except Exception as e:
                st.error(f"Error al cargar remito: {e}")

# --- VISTA DE LA PLANILLA ---
st.divider()
if st.checkbox("Ver estado actual de la planilla"):
    try:
        df_vista = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
        st.dataframe(df_vista, use_container_width=True, hide_index=True)
    except:
        st.info("No se pudo cargar la vista previa.")
