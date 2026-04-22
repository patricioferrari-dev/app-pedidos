import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Sistema de Pedidos", page_icon="📝")

st.title("📝 Registro de Pedidos")

# URL de tu hoja (la misma que pusiste en Secrets)
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit?pli=1#gid=0"

# Establecer conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulario de entrada
with st.form("nuevo_pedido"):
    st.subheader("Datos del Pedido")
    solicitante = st.text_input("Nombre del Solicitante")
    material = st.text_input("Material solicitado")
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
    
    submit = st.form_submit_button("Guardar Pedido")

    if submit:
        if solicitante and material:
            nuevo_dato = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Solicitante": solicitante,
                "Material": material,
                "Cantidad": cantidad,
                "Prioridad": prioridad
            }])

            try:
                # 1. Leer datos existentes
                df_existente = conn.read(spreadsheet=URL_HOJA, ttl=0) # ttl=0 evita que use datos viejos de memoria
                
                # 2. Combinar con el nuevo
                df_actualizado = pd.concat([df_existente, nuevo_dato], ignore_index=True)
                
                # 3. Subir a Google Sheets (Aquí es donde daba el error)
                conn.update(spreadsheet=URL_HOJA, data=df_actualizado)
                
                st.success("✅ ¡Guardado en Drive con éxito!")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("Por favor rellena todos los campos.")

# --- MOSTRAR TABLA ---
st.divider()
st.subheader("📋 Pedidos en la Base de Datos")
try:
    # Leer para mostrar (también pasando la URL)
    datos = conn.read(spreadsheet=URL_HOJA)
    if not datos.empty:
        st.dataframe(datos.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("La base de datos está vacía.")
except Exception as e:
    st.info("Aún no hay datos registrados o la hoja no es accesible.")
