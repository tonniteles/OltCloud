import API_OltCloud
import streamlit as st
import json

api = API_OltCloud.OltCloudAPI()

st.set_page_config(page_title="Consulta de ONU/ONT por Contrato", layout="wide")
st.title("🔍 Consulta de ONU/ONT por Contrato")
input_text= st.text_input("Entre com o número do contrato")
if st.button("Buscar ONU/ONT"):
    onu_info = api.get_ont(api.get_ontID_by_contrato(input_text))
    #print(onu_info)
    onu_info = onu_info['equipment'] if onu_info else None
    #print(json.dumps(onu_info, indent=3))
    if onu_info:
        st.subheader("Infomações da ONU/ONT (OLTCLOUD):")
        #st.json(onu_info)
        st.write(f'''
                 Contrato: {input_text}<br>
                 Serial Number: {onu_info['serial_number']}<br>
                 ONU ID: {onu_info['id']}<br>
                 Device Alias: {onu_info['device_alias']}<br>
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
                SLOT/PON/ONU ID: {onu_info['slot/pon/onu_id']}
        ''', unsafe_allow_html=True)
    else:
        st.error("Nenhuma ONU/ONT encontrada para o número do contrato informado.")