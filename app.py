import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import datetime

# 1. Autenticación con OAuth
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "creds/client_secret.json"
TOKEN_FILE = "creds/token.pickle"

def autenticar():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)
    return creds

# 2. Cargar Google Sheet
@st.cache_data(show_spinner=False)
def cargar_datos(creds):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key("18eBkLc9V4547Qz7SkejfRSwsWp3mCw4Y")
    ws = sh.sheet1
    df = pd.DataFrame(ws.get_all_records())
    return df, ws

# 3. Dropdowns
motivos = [
    "CAMBIO DE PRODUCTO", "ERRORES SELECCIONANDO CLIENTES", "FACTURAS SIN NCF",
    "CLIENTE NO PIDIO ESO", "CLIENTE NO LO QUISO", "CLIENTE NO LO USO",
    "FCT NO SE PUEDE MODIFICAR", "ERROR EN TIPO DE PRODUCTO", "FALTA DE TIEMPO",
    "MERCANCIA AVERIADA", "MOTOR AVERIADO", "NO SE MONTO", "NO HAY INVENTARIO",
    "NO RECIBIDO POR EL CLIENTE", "CLIENTE NO REVIBE ESE DIA"
]

mensajeros = {
    "IDM-MS-01": "Juan Jose",
    "IDM-MS-02": "Claudio Castillo",
    "IDM-MS-03": "Enemencio Hernnadez"
}

# 4. Main
st.title("📝 Gestión de Devoluciones")

creds = autenticar()
df, ws = cargar_datos(creds)

# Agrega columnas si no existen
for col in ["Mensajero", "Motivo Devolucion"]:
    if col not in df.columns:
        df[col] = ""

st.info("Edita las columnas de 'Mensajero' y 'Motivo Devolución' directamente en la tabla.")

# UI: Editor
editable_df = st.data_editor(
    df,
    column_config={
        "Mensajero": st.column_config.SelectboxColumn("Mensajero", options=list(mensajeros.keys())),
        "Motivo Devolucion": st.column_config.SelectboxColumn("Motivo de Devolución", options=motivos)
    },
    num_rows="dynamic"
)

# Guardar cambios
if st.button("💾 Guardar Cambios"):
    values = [editable_df.columns.tolist()] + editable_df.values.tolist()
    ws.update("A1", values)
    st.success("Cambios guardados en Google Sheets.")

