#app.py:
import streamlit as st
from utils import raspar_dados

st.title("Web Scraping of Aparments")

# Seleção do site
site = st.selectbox("Selecione o site", ["homegate", "immoscout24"])

# Seleção do tipo de transação
tipo = st.radio("Tipo de transação", ["alugar", "comprar"])

# Seleção da cidade
cidade = st.selectbox("Selecione a cidade", ["Geneve", "Zurich"])

# Botão para iniciar a raspagem
if st.button("Iniciar Raspagem"):
    st.write(f"Iniciando a raspagem para {tipo} em {cidade} no site {site}...")
    df = raspar_dados(site, tipo, cidade)
    st.write(df)
    st.success("Raspagem concluída!")
