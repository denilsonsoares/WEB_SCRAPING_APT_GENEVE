# app.py
import streamlit as st
import os
import pandas as pd
from utils_extract import raspar_dados
from utils_treat import tratar_dados_homegate, tratar_dados_immoscout24

st.title("Web Scraping of Apartments")

# Seleção do modo: raspagem ou tratamento de dados
modo = st.radio("Selecione o modo", ["Raspagem", "Tratamento de Dados"])

if modo == "Raspagem":
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

elif modo == "Tratamento de Dados":
    st.write("Tratando os dados na pasta 'dados brutos'...")

    # Diretórios
    pasta_brutos = "dados_brutos"
    pasta_tratados = "dados_tratados"

    # Verifica se a pasta de dados tratados existe, se não, cria
    if not os.path.exists(pasta_tratados):
        os.makedirs(pasta_tratados)

    # Lista os arquivos na pasta 'dados brutos'
    arquivos = os.listdir(pasta_brutos)

    # Mostrar os arquivos que serão tratados
    st.write("Arquivos a serem tratados:")
    st.write(arquivos)

    # Botão para iniciar o tratamento
    if st.button("Iniciar Tratamento"):
        # Tratamento dos arquivos
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(pasta_brutos, arquivo)

            if "homegate" in arquivo:
                tratar_dados_homegate(caminho_arquivo, pasta_tratados)
            elif "immoscout24" in arquivo:
                tratar_dados_immoscout24(caminho_arquivo, pasta_tratados)

        st.success("Dados tratados e salvos na pasta 'dados tratados'!")
