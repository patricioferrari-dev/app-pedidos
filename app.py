import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Control de Stock Inteligente", layout="wide")

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

st.title("📦 Sistema de Inventario con Lógica de Stock")

# --- FILA SUPERIOR: FECHA Y TIPO ---
fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
col_f1, col_f2 = st.columns([1, 1])

with col_f1:
    st.write(f"📅 **Fecha Automática:** {fecha_hoy}")

with col_f2:
    tipo_movimiento = st.selectbox(
        "Tipo de movimiento",
        [
            "Pedido de materiales", 
            "Devolución", 
            "Devolución por fallas", 
            "Otros"
        ],
        label_visibility="collapsed"
    )

st.markdown("---")

# --- FILA DE CARGA: CODIGO, DESCRIPCION, CANTIDAD Y BOTON ---
c1, c2, c3, c4 = st.columns([2, 4, 1.5, 1.5])

with c1:
    codigo_input = st.text_input("Código", placeholder="Escribe el código...").strip()

descripcion_detectada = ""
producto_valido = False

if codigo_input:
    if codigo_input in CATALOGO:
        descripcion_detectada = CATALOGO[codigo_input]
        producto_valido = True
    else:
        descripcion_detectada = "❌ Código no encontrado"

with c2:
    st.text_input("Descripción", value=descripcion_detectada, disabled=True)

with c3:
    cantidad_input = st.number_input("Cantidad", min_value=0, step=1)

with c4:
    st.write(" ") 
    boton_cargar = st.button("📥 Cargar", use_container_width=True)

# --- LÓGICA DE PROCESAMIENTO Y GUARDADO ---
if boton_cargar:
    if producto_valido and cantidad_input > 0:
        
        # LÓGICA DE SIGNOS:
        # Si es devolución por fallas, lo guardamos como negativo para que reste al sumar la columna
        cantidad_final = cantidad_input
        if tipo_movimiento == "Devolución por fallas":
            cantidad_final = cantidad_input * -1
            mensaje_exito = f"📉 Descuento registrado: {descripcion_detectada} ({cantidad_final})"
        else:
            mensaje_exito = f"📈 Ingreso registrado: {descripcion_detectada} (+{cantidad_final})"

        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Tipo": tipo_movimiento,
            "Codigo": codigo_input,
            "Descripcion": descripcion_detectada,
            "Cantidad": cantidad_final  # Aquí se guarda con el signo correcto
        }])
        
        try:
            nombre_pestaña = "Hoja1"
            df_historial = conn.read(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, ttl=0)
            df_final = pd.concat([df_historial, nuevo_registro], ignore_index=True)
            
            conn.update(spreadsheet=URL_HOJA, worksheet=nombre_pestaña, data=df_final)
            
            st.toast(mensaje_exito, icon="🚀")
            if cantidad_final < 0:
                st.warning(f"Se han descontado {cantidad_input} unidades por falla.")
            else:
                st.success(f"Se han sumado {cantidad_input} unidades.")
            
            st.rerun() 
        except Exception as e:
            st.error(f"Error al conectar: Revisa que la pestaña se llame 'Hoja1'")
    else:
        if not producto_valido and codigo_input:
            st.warning("⚠️ Código inválido.")
        elif cantidad_input <= 0:
            st.warning("⚠️ Cantidad debe ser mayor a 0.")

# --- TABLA DE ÚLTIMOS MOVIMIENTOS ---
st.subheader("📋 Historial de Movimientos")
try:
    historial = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    if not historial.empty:
        # Aplicamos un estilo visual: cantidades negativas en rojo (opcional)
        st.dataframe(historial.iloc[::-1].head(10), use_container_width=True, hide_index=True)
        
        # EXTRA: Cálculo de Stock Total del producto actual
        if producto_valido:
            stock_total = historial[historial["Codigo"] == codigo_input]["Cantidad"].sum()
            st.metric(label=f"Stock Actual de {descripcion_detectada}", value=int(stock_total))
except:
    pass
