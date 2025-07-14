import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# Configuración
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_ID = "18eBkLc9V4547Qz7SkejfRSwsWp3mCw4Y"  # Reemplaza con tu ID
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
    # Limpiar estado previo
    if "auth_initialized" not in st.session_state:
        st.session_state.clear()
        st.session_state["auth_initialized"] = True
    
    # 1. Verificar credenciales existentes
    if "credentials" in st.session_state:
        try:
            creds_info = json.loads(st.session_state["credentials"]) if isinstance(st.session_state["credentials"], str) else st.session_state["credentials"]
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
            
            # Verificación rápida de permisos
            try:
                gc = gspread.authorize(creds)
                gc.open_by_key(SHEET_ID)  # Prueba de acceso
                return creds
            except Exception as e:
                st.error(f"Error de permisos: {str(e)}")
                del st.session_state["credentials"]
                st.rerun()
                
        except Exception as e:
            st.error(f"Error en credenciales: {str(e)}")
            del st.session_state["credentials"]
            st.rerun()

    # 2. Configurar flujo OAuth
    flow = Flow.from_client_config(
        client_config={
            "web": st.secrets["google_oauth"]
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["google_oauth"]["redirect_uris"][0]
    )

    # 3. Manejar código de autorización
    if "code" in st.query_params:
        try:
            flow.fetch_token(code=st.query_params["code"])
            
            # Guardar credenciales completas
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

    # 4. Iniciar flujo de autorización
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    st.link_button("🔑 Autorizar con Google", auth_url)
    st.stop()

@st.cache_data(show_spinner=False, hash_funcs={Credentials: lambda _: None}, ttl=300)
def cargar_datos(creds):
    try:
        gc = gspread.authorize(creds)
        
        # Verificar acceso
        try:
            sh = gc.open_by_key(SHEET_ID)
        except gspread.exceptions.APIError as e:
            st.error(f"Error de acceso a la hoja. Verifica que esté compartida con:")
            st.error("883052339618-4qdc0altj75tr3o1m4q78nesidp3lrhq@developer.gserviceaccount.com")
            st.error(f"Detalle: {str(e)}")
            st.stop()
            
        # Obtener hoja
        try:
            ws = sh.worksheet(SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.sheet1  # Usar primera hoja si no existe
            
        return pd.DataFrame(ws.get_all_records()), ws
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        st.stop()

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
                    "Mensajero", 
                    options=list(mensajeros.keys())
                ),
                "Motivo Devolucion": st.column_config.SelectboxColumn(
                    "Motivo de Devolución", 
                    options=motivos
                )
            },
            num_rows="dynamic"
        )

        if st.button("💾 Guardar Cambios"):
            try:
                values = [editable_df.columns.tolist()] + editable_df.values.tolist()
                ws.update("A1", values)
                st.success("Cambios guardados correctamente!")
                st.cache_data.clear()  # Limpiar caché
            except Exception as e:
                st.error(f"Error al guardar: {str(e)}")

if __name__ == "__main__":
    main()
