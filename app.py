import streamlit as st
import pandas as pd
import gspread
import json
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# OAuth scopes
# Configuración
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Google Sheet ID and sheet name
SHEET_ID = "18eBkLc9V4547Qz7SkejfRSwsWp3mCw4Y"
SHEET_ID = "TU-ID-DE-HOJA"
SHEET_NAME = "Sheet1"

# Dropdown lists
motivos = [
    "CAMBIO DE PRODUCTO", "ERRORES SELECCIONANDO CLIENTES", "FACTURAS SIN NCF",
    "CLIENTE NO PIDIO ESO", "CLIENTE NO LO QUISO", "CLIENTE NO LO USO",
    "FCT NO SE PUEDE MODIFICAR", "ERROR EN TIPO DE PRODUCTO", "FALTA DE TIEMPO",
    "MERCANCIA AVERIADA", "MOTOR AVERIADO", "NO SE MONTO", "NO HAY INVENTARIO",
    "NO RECIBIDO POR EL CLIENTE", "CLIENTE NO RECIBE ESE DIA"
]

mensajeros = {
    "IDM-MS-01": "Juan Jose",
    "IDM-MS-02": "Claudio Castillo",
    "IDM-MS-03": "Enemencio Hernnadez"
}

def autenticar():
    # Initialize the OAuth flow
    if "credentials" in st.session_state:
        return Credentials.from_authorized_user_info(
            st.session_state["credentials"], SCOPES)
    
flow = Flow.from_client_config(
client_config={
            "web": st.secrets["google_oauth"]
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": st.secrets["google_oauth"]["redirect_uris"]
            }
},
scopes=SCOPES,
redirect_uri=st.secrets["google_oauth"]["redirect_uris"][0]
)

    # Check for existing credentials
    if "credentials" in st.session_state:
        try:
            return Credentials.from_authorized_user_info(
                json.loads(st.session_state["credentials"]),
                SCOPES
            )
        except Exception as e:
            st.error(f"Error loading credentials: {str(e)}")
            del st.session_state["credentials"]
            st.rerun()
    if "code" not in st.query_params:
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.link_button("🔑 Autorizar con Google", auth_url)
        st.stop()

    # Check for authorization code in URL
    query_params = st.query_params
    if "code" in query_params:
        try:
            # Exchange the authorization code for tokens
            flow.fetch_token(code=query_params["code"])
            
            # Store the credentials in session state
            st.session_state["credentials"] = flow.credentials.to_json()
            
            # Clear the code from URL
            st.query_params.clear()
            
            # Reload the page without the code parameter
            st.rerun()
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            st.stop()
    
    # If no credentials and no code, start authorization flow
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    st.link_button("Authorize with Google", auth_url)
    st.stop()

@st.cache_data(show_spinner=False)
def cargar_datos(creds):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    df = pd.DataFrame(ws.get_all_records())
    return df, ws
    flow.fetch_token(code=st.query_params["code"])
    st.session_state["credentials"] = flow.credentials.to_json()
    st.query_params.clear()
    st.rerun()

def main():
    st.title("📝 Gestión de Devoluciones")
    
    st.title("Gestor de Devoluciones")
creds = autenticar()
    if creds:
        df, ws = cargar_datos(creds)

        # Add columns if they don't exist
        for col in ["Mensajero", "Motivo Devolucion"]:
            if col not in df.columns:
                df[col] = ""

        st.info("Edita las columnas 'Mensajero' y 'Motivo Devolución'.")

        editable_df = st.data_editor(
            df,
            column_config={
                "Mensajero": st.column_config.SelectboxColumn(
                    "Mensajero", options=list(mensajeros.keys())
                ),
                "Motivo Devolucion": st.column_config.SelectboxColumn(
                    "Motivo de Devolución", options=motivos
                ),
            },
            num_rows="dynamic"
        )

        if st.button("💾 Guardar Cambios"):
            values = [editable_df.columns.tolist()] + editable_df.values.tolist()
            ws.update("A1", values)
            st.success("Cambios guardados en Google Sheets.")
    
    # Tu lógica de aplicación aquí
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = pd.DataFrame(sheet.get_all_records())
    st.dataframe(data)

if __name__ == "__main__":
main()
