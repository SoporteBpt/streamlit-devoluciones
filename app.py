import streamlit as st
import pandas as pd
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Google Sheet ID y nombre hoja
SHEET_ID = "18eBkLc9V4547Qz7SkejfRSwsWp3mCw4Y"
SHEET_NAME = "Sheet1"

# Listas desplegables
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
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "auth_uri": st.secrets["google_oauth"]["auth_uri"],
                "token_uri": st.secrets["google_oauth"]["token_uri"],
                "redirect_uris": st.secrets["google_oauth"]["redirect_uris"]
            }
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["google_oauth"]["redirect_uris"][0]
    )
    
    if "credentials" not in st.session_state:
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            include_granted_scopes="true"
        )
        st.session_state["auth_url"] = auth_url
        st.link_button("🔑 Autorizar con Google", auth_url)
        st.stop()
    
    elif "code" in st.experimental_get_query_params():
        code = st.experimental_get_query_params()["code"]
        flow.fetch_token(code=code)
        st.session_state["credentials"] = flow.credentials.to_json()
        st.experimental_set_query_params()
        st.rerun()
    
    if "credentials" in st.session_state:
        return Credentials.from_authorized_user_info(
            json.loads(st.session_state["credentials"]),
            SCOPES
        )

@st.cache_data(show_spinner=False)
def cargar_datos(creds):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    df = pd.DataFrame(ws.get_all_records())
    return df, ws

def main():
    st.title("📝 Gestión de Devoluciones")
    
    creds = autenticar()
    if creds:
        df, ws = cargar_datos(creds)

        # Agregar columnas si no existen
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

if __name__ == "__main__":
    main()
