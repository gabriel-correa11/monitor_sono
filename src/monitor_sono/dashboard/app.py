"""RF08-RF11, RNF06, RNF07 — Dashboard Streamlit.

Rodar com: streamlit run src/monitor_sono/dashboard/app.py
"""

import streamlit as st

from monitor_sono import config

st.set_page_config(page_title="Monitor de Sono")
st.title("Monitor de Sono")
st.info(config.AVISO_NAO_DIAGNOSTICO)  # RNF07

st.header("Sessões anteriores")   # RF10
st.write("A implementar.")

st.header("Resumo da sessão")     # RF09
st.write("A implementar.")

st.header("Linha do tempo")       # RF08
st.write("A implementar.")

st.header("Relatório")            # RF11
st.write("A implementar.")
