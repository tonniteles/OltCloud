import requests
import streamlit as st

import API_OltCloud

if "onu_info" not in st.session_state:
    st.session_state.onu_info = None
if "search_attempted" not in st.session_state:
    st.session_state.search_attempted = False


@st.cache_resource
def get_api():
    return API_OltCloud.OltCloudAPI()


def get_search_type(option):
    return {
        "Número do Contrato": "device_alias",
        "Número de Série": "serial",
        "Endereço MAC": "mac",
    }.get(option, "device_alias")


def format_contract(device_alias):
    if not device_alias:
        return "—"
    return device_alias.split("-")[0]


st.set_page_config(page_title="Consulta de ONU/ONT", layout="wide")
st.title("🔍 Consulta de ONU/ONT")

with st.form(key="search_form", enter_to_submit=True, border=False):
    search_option = st.radio(
        "Selecione o tipo de consulta:",
        ("Número do Contrato", "Número de Série", "Endereço MAC"),
        index=0,
        horizontal=True,
    )
    col1, col2 = st.columns([1, 2])

    with col1:
        input_text = st.text_input("Digite a Busca: ")

    with col2:
        st.write("")
        st.write("")
        submit_button = st.form_submit_button(label="Buscar")

if submit_button:
    if not input_text.strip():
        st.error("Por favor, insira um valor para a busca.")
    else:
        api = get_api()
        search_type = get_search_type(search_option)
        st.session_state.search_attempted = True

        ont_id = api.get_ontID(input_text, search_type)
        if ont_id is None:
            st.session_state.onu_info = None
            if not api.onts:
                st.warning(
                    "Cache de ONUs vazio. Verifique se o script import_onus.py está em execução."
                )
        else:
            try:
                response = api.get_ont(ont_id)
                equipment = response.get("equipment") if response else None
                st.session_state.onu_info = equipment
            except requests.HTTPError as e:
                st.session_state.onu_info = None
                status = e.response.status_code if e.response is not None else "?"
                st.error(f"Erro na API (HTTP {status}).")
            except requests.RequestException:
                st.session_state.onu_info = None
                st.error("Erro de ligação à API. Tente novamente.")
            except Exception as e:
                st.session_state.onu_info = None
                st.error(f"Erro inesperado: {e}")

if st.session_state.onu_info:
    info = st.session_state.onu_info

    st.subheader("📡 Informações da ONU/ONT")
    st.markdown(
        f"""
        **Contrato:** {format_contract(info.get('device_alias'))}  
        **Serial:** {info.get('serial_number')}  
        **ONU ID:** {info.get('id')}  
        **Model:** {info.get('model')}  
        **MAC:** {', '.join(info.get('macs', []))}
        """
    )

    st.subheader("⚙️ Parâmetros")
    st.markdown(
        f"""
        **Status:** {info.get('status')}  
        **RX:** {info.get('device_rx')} dBm  
        **TX:** {info.get('device_tx')} dBm  
        **OLT RX:** {info.get('olt_rx')} dBm  
        **Temperatura:** {info.get('temperature')} °C  
        **OLT:** {info.get('olt')}  
        **SLOT/PON/ONU:** {info.get('slot/pon/onu_id')}  
        **VLANs:** {', '.join(str(v) for v in info.get('vlans', []))}
        """
    )
elif st.session_state.search_attempted:
    st.warning("Nenhuma ONU/ONT encontrada.")
