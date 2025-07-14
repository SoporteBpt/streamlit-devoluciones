import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configuración
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "18eBkLc9V4547Qz7SkejfRSwsWp3mCw4Y"
SHEET_NAME = "Sheet1"

# ... (tus listas motivos y mensajeros permanecen igual)

def autenticar():
    if "credentials" in st.session_state:
        try:
            creds_info = json.loads(st.session_state["credentials"]) if isinstance(st.session_state["credentials"], str) else st.session_state["credentials"]
            return Credentials.from_authorized_user_info(creds_info, SCOPES)
        except Exception as e:
            st.error(f"Error en credenciales: {str(e)}")
            del st.session_state["credentials"]
            st.rerun()

    flow = Flow.from_client_config(
        client_config={
            "web": st.secrets["google_oauth"]
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["google_oauth"]["redirect_uris"][0]
    )

    if "code" in st.query_params:
        try:
            flow.fetch_token(code=st.query_params["code"])
            st.session_state["credentials"] = flow.credentials.to_json()
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Error de autenticación: {str(e)}")
            st.stop()

    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    st.link_button("🔑 Autorizar con Google", auth_url)
    st.stop()

# Solución 1: Usando hash_funcs
@st.cache_data(show_spinner=False, hash_funcs={Credentials: lambda _: None})
def cargar_datos(creds):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(SHEET_NAME)
    return pd.DataFrame(ws.get_all_records()), ws

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
            st.success("Cambios guardados correctamente!")

if __name__ == "__main__":
    main()
