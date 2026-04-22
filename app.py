import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

conn = st.connection("gsheets", type=GSheetsConnection)

# Para leer:
df = conn.read()

# Para guardar (en el botón de tu formulario):
if boton_pedido:
    # ... (tu lógica de crear nuevo_df) ...
    df_final = pd.concat([df, nuevo_df], ignore_index=True)
    conn.update(data=df_final)
    st.success("¡Guardado con éxito!")
