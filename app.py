import API_OltCloud
import streamlit as st
import json

api = API_OltCloud.OltCloudAPI()

st.set_page_config(page_title="Consulta de ONU/ONT", layout="wide")
st.title("🔍 Consulta de ONU/ONT")

#search_option = st.radio("Selecione o tipo de consulta:", ('Número do Contrato', 'Número de Série', 'Endereço MAC'), index=0, horizontal=True)
with st.form(key='search_form'):
    search_option = st.radio("Selecione o tipo de consulta:", ('Número do Contrato', 'Número de Série', 'Endereço MAC'), index=0, horizontal=True)
    col1, col2 = st.columns([1,1])
    with col1:
        input_text = st.text_input("Digite a Busca: ")
    with col2:
        st.write("")  # Espaço para alinhar o botão
        st.write("")  # Espaço para alinhar o botão
        submit_button = st.form_submit_button(label='Buscar')

if submit_button:
    match search_option:
        case 'Número do Contrato':
            search_type = 'device_alias'
        case 'Número de Série':
            search_type = 'serial'
        case 'Endereço MAC':
            search_type = 'mac'

    if not input_text:
        st.error("Por favor, insira um valor para a busca.")
    else:
        onu_info = api.get_ont(api.get_ontID(input_text, search_type))

    onu_info = onu_info['equipment'] if onu_info else None
    #print(json.dumps(onu_info, indent=3))
    if onu_info:
        st.subheader("Infomações da ONU/ONT (OLTCLOUD):")
        #st.json(onu_info)
        st.write(f'''
                 Contrato: {onu_info['device_alias']}<br>
                 Serial Number: {onu_info['serial_number']}<br>
                 ONU ID: {onu_info['id']}<br>
                 MAC: {', '.join(onu_info['macs'])}
                ''', unsafe_allow_html=True)
        #st.write(f"Model: {onu_info['model']}")
        st.subheader("Parametros da ONU/ONT:")
        st.write(f'''
                Status: {onu_info['status']}<br>
                RX Power: {onu_info['device_rx']} dBm<br>
                TX Power: {onu_info['device_tx']} dBm<br>
                OLT RX Power: {onu_info['olt_rx']} dBm<br>
                Temperature: {onu_info['temperature']} °C<br>
                OLT: {onu_info['olt']}<br>
                SLOT/PON/ONU ID: {onu_info['slot/pon/onu_id']}<br>
                VLAN: {', '.join(onu_info['vlans'])}
        ''', unsafe_allow_html=True)
    else:
        st.error("Nenhuma ONU/ONT encontrada para o número do contrato informado.")