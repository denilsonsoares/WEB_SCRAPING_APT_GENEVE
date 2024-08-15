import streamlit as st
import os
import pandas as pd
from utils_extract import raspar_dados, set_parar_raspagem
from utils_treat import *
# Título do aplicativo
st.title("Web Scraping de Apartamentos")

# Seleção do modo: Raspagem ou Tratamento de Dados
modo = st.radio("Selecione o modo", ["Raspagem", "Tratamento de Dados"])

# Modo de Raspagem
if modo == "Raspagem":
    # Seleção do site
    site = st.selectbox("Selecione o site", ["homegate", "immoscout24"])

    # Seleção do tipo de transação
    tipo = st.radio("Tipo de transação", ["alugar", "comprar"])

    # Seleção da cidade
    cidade = st.selectbox("Selecione a cidade", ["Geneve", "Zurich"])

    # Botão para iniciar a raspagem
    iniciar_raspagem = st.button("Iniciar Raspagem")

    # Botão para parar a raspagem
    parar_raspagem = st.button("Parar Raspagem")

    if iniciar_raspagem:
        # Reseta a variável global de controle de raspagem
        set_parar_raspagem(False)

        # Informa o usuário sobre o início da raspagem
        st.write(f"Iniciando a raspagem para {tipo} em {cidade} no site {site}...")

        # Realiza a raspagem de dados
        df = raspar_dados(site, tipo, cidade)

        # Exibe os dados raspados
        st.write(df)

        st.success("Raspagem concluída!")

    if parar_raspagem:
        # Sinaliza para parar a raspagem
        set_parar_raspagem(True)
        st.warning("Raspagem interrompida!")

# Modo de Tratamento de Dados
elif modo == "Tratamento de Dados":
    # Informa que o tratamento de dados será realizado na pasta especificada
    st.write("Tratando os dados na pasta 'dados brutos'...")

    # Diretórios
    pasta_brutos = "dados_brutos"
    pasta_tratados = "dados_tratados"

    # Verifica se a pasta de dados tratados existe; caso contrário, cria a pasta
    if not os.path.exists(pasta_tratados):
        os.makedirs(pasta_tratados)

    # Lista os arquivos na pasta 'dados brutos'
    arquivos = os.listdir(pasta_brutos)

    # Exibe os arquivos que serão tratados
    st.write("Arquivos a serem tratados:")
    st.write(arquivos)

    # Botão para iniciar o tratamento de dados
    if st.button("Iniciar Tratamento"):
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(pasta_brutos, arquivo)

            # Verifica o site e realiza o tratamento específico
            if "homegate" in arquivo:
                tratar_dados_homegate(caminho_arquivo, pasta_tratados)
            elif "immoscout24" in arquivo:
                tratar_dados_immoscout24(caminho_arquivo, pasta_tratados)

        st.success("Dados tratados e salvos na pasta 'dados tratados'!")
