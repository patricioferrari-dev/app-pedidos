import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Stock Fijo", layout="centered")

# --- 1. TU CATÁLOGO (Debe coincidir con la columna "Artículo" de tu Excel) ---
CATALOGO = {
    "30032": "Tarugo de 8mm para ladrillo hueco",
    "012009U": "Fuentes 12V-1,5A para decos UHF Inspur Model STB STB-6755TI",
    "13008": "CONTROL REMOTO PARA DECO SAGECOM DCWMI303. CON BOTONES YT + NETFLIX",
    "13012": "CONTROL REMOTO POR VOZ PARA DECO SAGEMCOM V2",
    "13013": "CONTROL REMOTO POR VOZ V3 PARA DECO SAGEMCOM 362 - VSB3930",
}

URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📊 Control de Inventario por Columnas")

# --- INTERFAZ VERTICAL ---
# 1. Selección de Columna a afectar (basado en tu foto)
tipo_movimiento = st.selectbox(
    "Seleccione qué valor desea cargar:",
    ["Cumplidas", "STOCK", "CLOUD", "Pedido"]
)

# 2. Código
codigo_input = st.text_input("Ingrese el Código del Artículo:").strip()

# Verificación
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
cantidad_input = st.number_input("Cantidad a ingresar:", min_value=0, step=1)

# 5. Botón
boton_cargar = st.button("💾 Actualizar Planilla", use_container_width=True)

# --- LÓGICA DE ACTUALIZACIÓN ---
if boton_cargar:
    if producto_valido and cantidad_input > 0:
        try:
            # Leer la hoja completa
            df = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
            
            # Asegurarse de que el Código sea tratado como texto para comparar
            df['Código'] = df['Código'].astype(str).str.strip()
            
            # Buscar la fila del producto
            if codigo_input in df['Código'].values:
                # Actualizar la celda específica (Fila del código, Columna elegida)
                # Sumamos el valor nuevo al valor que ya existía (opcional, si quieres reemplazar quita el '+')
                valor_actual = df.loc[df['Código'] == codigo_input, tipo_movimiento].values[0]
                
                # Si la celda está vacía (NaN), la tratamos como 0
                if pd.isna(valor_actual): valor_actual = 0
                
                df.loc[df['Código'] == codigo_input, tipo_movimiento] = valor_actual + cantidad_input
                
                # Guardar toda la tabla actualizada
                conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df)
                
                st.success(f"✅ Se actualizaron {cantidad_input} unidades en '{tipo_movimiento}' para {descripcion_detectada}")
                st.balloons()
            else:
                st.error("El código existe en el catálogo pero no se encontró la fila en el Excel. Revisa los encabezados.")
            
        except Exception as e:
            st.error(f"Error al actualizar: {e}")
    else:
        st.warning("Verifique el código y la cantidad.")

# --- VISTA PREVIA DE LA TABLA ---
st.divider()
st.subheader("📋 Estado Actual de la Planilla")
try:
    df_vista = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    st.dataframe(df_vista, use_container_width=True, hide_index=True)
except:
    st.info("Carga el primer dato para ver la tabla.")
