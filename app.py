import streamlit as st
import gspread
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

st.session_state.clear()  # Agrega esto al inicio de tu app
# Configuración
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "TU-ID-DE-HOJA"
SHEET_NAME = "Sheet1"

def autenticar():
    # Verificar si ya estamos autenticados
    if "credentials" in st.session_state:
        try:
            # Asegurarnos que las credenciales son un diccionario
            if isinstance(st.session_state["credentials"], str):
                creds_info = json.loads(st.session_state["credentials"])
            else:
                creds_info = st.session_state["credentials"]
                
            return Credentials.from_authorized_user_info(creds_info, SCOPES)
        except Exception as e:
            st.error(f"Error cargando credenciales: {str(e)}")
            del st.session_state["credentials"]
            st.rerun()

    # Configurar el flujo OAuth
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
    # Manejar el código de autorización
    if "code" in st.query_params:
        try:
            flow.fetch_token(code=st.query_params["code"])
            
            # Guardar TODAS las credenciales en formato diccionario
            st.session_state["credentials"] = {
                "token": flow.credentials.token,
                "refresh_token": flow.credentials.refresh_token,
                "token_uri": flow.credentials.token_uri,
                "client_id": flow.credentials.client_id,
                "client_secret": flow.credentials.client_secret,
                "scopes": flow.credentials.scopes
            }
            
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Error de autenticación: {str(e)}")
            st.stop()

    # Iniciar flujo de autenticación
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    st.link_button("🔑 Autorizar con Google", auth_url)
    st.stop()
    
    flow.fetch_token(code=st.query_params["code"])
    st.session_state["credentials"] = flow.credentials.to_json()
    st.query_params.clear()
    st.rerun()

def main():
    st.title("Gestor de Devoluciones")
    creds = autenticar()
    
    # Tu lógica de aplicación aquí
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = pd.DataFrame(sheet.get_all_records())
    st.dataframe(data)

if __name__ == "__main__":
    main()
