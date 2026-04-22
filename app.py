import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Materiales", page_icon="📦")

st.title("📦 Control de Materiales")

# URL de tu hoja (Asegúrate de que sea la misma)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"

# Establecer conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FORMULARIO DE REGISTRO ---
with st.form("nuevo_registro"):
    st.subheader("Nuevo Movimiento")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de ingreso", 
                            ["Pedido de materiales", "Devolucion por fallas", "Otros"])
    with col2:
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
    
    codigo = st.text_input("Código del Producto").upper().strip()
    descripcion = st.text_area("Descripción del Material")
    
    submit = st.form_submit_button("Registrar en Base de Datos")

    if submit:
        if codigo and descripcion:
            # Crear el nuevo registro con tus nuevas columnas
            nuevo_dato = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Tipo": tipo,
                "Codigo": codigo,
                "Descripcion": descripcion,
                "Cantidad": cantidad
            }])

            try:
                # 1. Leer datos existentes
                df_existente = conn.read(spreadsheet=URL_HOJA, ttl=0)
                
                # 2. Combinar
                df_actualizado = pd.concat([df_existente, nuevo_dato], ignore_index=True)
                
                # 3. Guardar
                conn.update(spreadsheet=URL_HOJA, data=df_actualizado)
                
                st.success(f"✅ ¡{codigo} registrado correctamente!")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("⚠️ Por favor, ingresa el Código y la Descripción.")

# --- VISUALIZACIÓN DE DATOS ---
st.divider()
st.subheader("📋 Historial de Movimientos")

try:
    # Leer para mostrar
    datos = conn.read(spreadsheet=URL_HOJA, ttl=0)
    if not datos.empty:
        # Ordenar para que el último registro aparezca arriba
        st.dataframe(datos.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros en la base de datos.")
except Exception as e:
    st.info("Esperando los primeros datos...")
