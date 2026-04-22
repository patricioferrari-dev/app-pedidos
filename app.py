import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Pedidos de Materiales", page_icon="📝")

st.title("📝 Sistema de Pedidos de Materiales")

# Inicializar una lista de pedidos en la memoria de la app
if 'pedidos' not in st.session_state:
    st.session_state.pedidos = []

# Formulario de entrada
with st.form("nuevo_pedido"):
    st.subheader("Realizar Nuevo Pedido")
    material = st.text_input("Nombre del Material")
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
    solicitante = st.text_input("Nombre del Solicitante")
    
    boton_pedido = st.form_submit_button("Enviar Pedido")

    if boton_pedido:
        if material and solicitante:
            nuevo_item = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Solicitante": solicitante,
                "Material": material,
                "Cantidad": cantidad,
                "Prioridad": prioridad
            }
            st.session_state.pedidos.append(nuevo_item)
            st.success("✅ Pedido registrado exitosamente.")
        else:
            st.error("⚠️ Por favor, completa todos los campos.")

# Mostrar los pedidos registrados
st.divider()
st.subheader("📋 Lista de Pedidos Actuales")

if st.session_state.pedidos:
    df = pd.DataFrame(st.session_state.pedidos)
    st.dataframe(df, use_container_width=True)
    
    # Botón para descargar como CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar Pedidos (CSV)", csv, "pedidos.csv", "text/csv")
else:
    st.info("No hay pedidos registrados todavía.")