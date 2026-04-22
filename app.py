import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(page_title="Pedidos a Google Sheets", page_icon="📊")

st.title("📊 Registro de Pedidos en Google Sheets")

# Crear conexión con la hoja de cálculo
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulario
with st.form("nuevo_pedido"):
    st.subheader("Realizar Nuevo Pedido")
    material = st.text_input("Nombre del Material")
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
    solicitante = st.text_input("Nombre del Solicitante")
    
    boton_pedido = st.form_submit_button("Guardar en Google Sheets")

    if boton_pedido:
        if material and solicitante:
            # 1. Crear el nuevo registro
            nuevo_registro = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Solicitante": solicitante,
                "Material": material,
                "Cantidad": cantidad,
                "Prioridad": prioridad
            }])

            try:
                # 2. Leer datos actuales de la nube
                datos_actuales = conn.read()
                
                # 3. Concatenar (unir) el nuevo registro
                # Si la hoja estaba vacía, simplemente usamos el nuevo_registro
                if datos_actuales is not None:
                    df_final = pd.concat([datos_actuales, nuevo_registro], ignore_index=True)
                else:
                    df_final = nuevo_registro
                
                # 4. Actualizar la hoja de Google
                conn.update(data=df_final)
                
                st.success("✅ ¡Pedido guardado en Google Drive!")
                st.balloons()
            except Exception as e:
                st.error(f"Error de conexión: {e}")
        else:
            st.error("⚠️ Completa todos los campos.")

# --- VISUALIZACIÓN ---
st.divider()
st.subheader("📋 Historial de Pedidos (Desde la Nube)")

try:
    # Leer y mostrar los datos actualizados
    df_nube = conn.read()
    if not df_nube.empty:
        # Mostramos los últimos pedidos primero
        st.dataframe(df_nube.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("La base de datos está vacía.")
except:
    st.warning("Aún no hay datos para mostrar.")
