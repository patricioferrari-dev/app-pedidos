import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Stock Vertical", layout="centered")

# --- 1. TU CATÁLOGO DE PRODUCTOS ---
CATALOGO = {
    "30032": "Cable",
    "40050": "Tornillo 2 pulgadas",
    "50010": "Pintura sintética blanca",
    "12345": "Herramienta de prueba",
}

# URL de tu hoja
URL_HOJA = "https://docs.google.com/spreadsheets/d/1zc4xSypiN1mmDZghgrCmn2ItzZVjLYBsUxw1VHetIB8/edit#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("📦 Gestión de Inventario")

# --- SECCIÓN DE ENTRADA VERTICAL ---
st.subheader("Registrar Movimiento")

# 1. Fecha (Informativa)
fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
st.write(f"📅 **Fecha:** {fecha_hoy}")

# 2. Tipo de Movimiento
tipo_movimiento = st.selectbox(
    "Seleccione el tipo de movimiento:",
    [
        "Pedido de materiales", 
        "Devolución", 
        "Devolución por fallas", 
        "Otros"
    ]
)

# 3. Código
codigo_input = st.text_input("Código del Producto:", placeholder="Ej: 30032").strip()

# Lógica de detección
descripcion_detectada = ""
producto_valido = False

if codigo_input:
    if codigo_input in CATALOGO:
        descripcion_detectada = CATALOGO[codigo_input]
        producto_valido = True
    else:
        descripcion_detectada = "❌ Código no encontrado"

# 4. Descripción (Auto-completada)
st.text_input("Descripción:", value=descripcion_detectada, disabled=True)

# 5. Cantidad
cantidad_input = st.number_input("Cantidad a ingresar:", min_value=0, step=1)

# 6. Botón de Carga (Ancho total)
st.write("") # Espacio
boton_cargar = st.button("📥 Cargar Registro", use_container_width=True)

# --- LÓGICA DE PROCESAMIENTO Y GUARDADO ---
if boton_cargar:
    if producto_valido and cantidad_input > 0:
        
        # Lógica de signos
        cantidad_final = cantidad_input
        if tipo_movimiento == "Devolución por fallas":
            cantidad_final = cantidad_input * -1
            mensaje_exito = f"📉 Descuento: {descripcion_detectada} ({cantidad_final})"
        else:
            mensaje_exito = f"📈 Ingreso: {descripcion_detectada} (+{cantidad_final})"

        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Tipo": tipo_movimiento,
            "Codigo": codigo_input,
            "Descripcion": descripcion_detectada,
            "Cantidad": cantidad_final
        }])
        
        try:
            nombre_pestaña = "Hoja1"
            df_historial = conn.read(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, ttl=0)
            df_final = pd.concat([df_historial, nuevo_registro], ignore_index=True)
            
            conn.update(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, data=df_final)
            
            st.toast(mensaje_exito, icon="🚀")
            if cantidad_final < 0:
                st.warning(f"Se han descontado {cantidad_input} unidades.")
            else:
                st.success(f"Se han sumado {cantidad_input} unidades.")
            
            st.rerun() 
        except Exception as e:
            st.error(f"Error al conectar con la hoja 'Hoja1'")
    else:
        if not producto_valido and codigo_input:
            st.warning("⚠️ El código no existe en el catálogo.")
        elif cantidad_input <= 0:
            st.warning("⚠️ La cantidad debe ser mayor a 0.")

# --- SECCIÓN DE HISTORIAL Y MÉTRICAS ---
st.markdown("---")
try:
    historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    if not historial.empty:
        # Stock Actual destacado
        if producto_valido:
            stock_total = historial[historial["Codigo"] == codigo_input]["Cantidad"].sum()
            st.metric(label=f"Stock Actual de {descripcion_detectada}", value=int(stock_total))
        
        st.subheader("📋 Últimos 10 Movimientos")
        st.dataframe(historial.iloc[::-1].head(10), use_container_width=True, hide_index=True)
except:
    pass
