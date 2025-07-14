import streamlit as st
import gspread
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configuración
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "TU-ID-DE-HOJA"
SHEET_NAME = "Sheet1"

def autenticar():
    if "credentials" in st.session_state:
        return Credentials.from_authorized_user_info(
            st.session_state["credentials"], SCOPES)
    
    flow = Flow.from_client_config(
        client_config={
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
    
    if "code" not in st.query_params:
        auth_url, _ = flow.authorization_url(prompt="consent")
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
