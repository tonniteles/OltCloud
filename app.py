import API_OltCloud
import streamlit as st

def get_api():
    return API_OltCloud.OltCloudAPI()

def get_search_type(option):
    return {
        'Número do Contrato': 'device_alias',
        'Número de Série': 'serial',
        'Endereço MAC': 'mac'
    }.get(option)

if "onu_info" not in st.session_state:
    st.session_state.onu_info = None

st.set_page_config(page_title="Consulta de ONU/ONT", layout="wide")
st.title("🔍 Consulta de ONU/ONT")

with st.form(key='search_form', enter_to_submit=True, border=False):
    search_option = st.radio(
        "Selecione o tipo de consulta:", 
        ('Número do Contrato', 'Número de Série', 'Endereço MAC'),
        index=0, 
        horizontal=True
    )
    col1, col2 = st.columns([1,2])

    with col1:
        input_text = st.text_input("Digite a Busca: ")

    with col2:
        st.write("")
        st.write("")
        submit_button = st.form_submit_button(label='Buscar')

    onu_info = None

    if submit_button:
        if not input_text:
            st.error("Por favor, insira um valor para a busca.")
            st.stop()

        api = get_api()
        search_type = get_search_type(search_option)

        try:
            ont_id = api.get_ontID(input_text, search_type)
            st.session_state.onu_info = api.get_ont(ont_id)
            st.session_state.onu_info = st.session_state.onu_info.get('equipment') if st.session_state.onu_info else None

        except Exception as e:
            st.error(f"Erro ao consultar API: {str(e)}")
            st.stop()
    
    if st.session_state.onu_info:
        st.subheader("📡 Informações da ONU/ONT")

        st.markdown(f"""
        **Contrato:** {st.session_state.onu_info.get('device_alias').split('-')[0]}  
        **Serial:** {st.session_state.onu_info.get('serial_number')}  
        **ONU ID:** {st.session_state.onu_info.get('id')}  
        **MAC:** {', '.join(st.session_state.onu_info.get('macs', []))}
        """)


        st.subheader("⚙️ Parâmetros")
        st.markdown(f"""
        **Status:** {st.session_state.onu_info.get('status')}  
        **RX:** {st.session_state.onu_info.get('device_rx')} dBm  
        **TX:** {st.session_state.onu_info.get('device_tx')} dBm  
        **OLT RX:** {st.session_state.onu_info.get('olt_rx')} dBm  
        """)

        st.markdown(f"""
        **Temperatura:** {st.session_state.onu_info.get('temperature')} °C  
        **OLT:** {st.session_state.onu_info.get('olt')}  
        **SLOT/PON/ONU:** {st.session_state.onu_info.get('slot/pon/onu_id')}  
        **VLANs:** {', '.join(st.session_state.onu_info.get('vlans', []))}
        """)
    else:
        st.warning("Nenhuma ONU/ONT encontrada.")