"""RF13, RF14, RF15, RNF07, RNF12 — Dashboard Streamlit.

Rodar com: streamlit run src/monitor_sono/dashboard/app.py
"""

import streamlit as st

from monitor_sono import config

st.set_page_config(page_title="Monitor de Sono")
st.title("Monitor de Sono")
st.info(config.AVISO_NAO_DIAGNOSTICO)  # RNF12

st.header("Sessões anteriores")         # RF14
st.write("A implementar.")

st.header("Resumo da sessão")           # RF13
st.write("A implementar.")

st.header("Comportamentos observados")  # RF13
st.write("A implementar.")

st.header("Estados estimados")          # RF13, RNF07
st.write("A implementar.")

st.header("Visibilidade")               # RF15
st.write("A implementar.")

st.header("Relatório")                  # RF14
st.write("A implementar.")
