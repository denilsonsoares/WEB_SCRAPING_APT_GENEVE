from datetime import datetime
import streamlit as st
import os
import pandas as pd
import zipfile
import io
import plotly.express as px
from utils_extract import raspar_dados, set_parar_raspagem
from utils_treat import *
from utils_analytics import *

# Título do aplicativo
st.title("Apartment Web Scraping")

# Seleção do modo: Raspagem, Tratamento de Dados ou Análise de Dados
modo = st.radio("Select mode", ["Scraping", "Data Processing", "Data Analysis"])

# Modo de Raspagem
if modo == "Scraping":
    # Seleção do site
    sites = st.multiselect("Select websites", ["homegate", "immoscout24"], default=["homegate", "immoscout24"])

    # Seleção do tipo de transação
    tipos = st.multiselect("Transaction types", ["alugar", "comprar"], default=["alugar", "comprar"])

    # Seleção da cidade
    cidades = st.multiselect("Select cities", ["Geneve", "Zurich"], default=["Geneve", "Zurich"])

    # Botão para iniciar a raspagem
    iniciar_raspagem = st.button("Start Scraping")

    # Botão para parar a raspagem
    parar_raspagem = st.button("Stop Scraping")

    if iniciar_raspagem:
        # Reseta a variável global de controle de raspagem
        set_parar_raspagem(False)

        # Loop sobre todas as combinações de site, tipo de transação e cidade
        for site in sites:
            for tipo in tipos:
                for cidade in cidades:
                    if parar_raspagem:
                        break

                    # Informa o usuário sobre o início da raspagem
                    st.write(f"Starting scraping {tipo} in {cidade} on the website {site}...")

                    # Realiza a raspagem de dados
                    df = raspar_dados(site, tipo, cidade)
                    # Exibe os dados raspados
                    st.write(df)
                    st.success(f"Scraping completed for {site}, {tipo}, {cidade}!")

        if parar_raspagem:
            st.warning("Scraping interrupted!")
        else:
            st.success("Scraping completed for all combinations!")

    if parar_raspagem:
        # Sinaliza para parar a raspagem
        set_parar_raspagem(True)
        st.warning("Scraping interrupted!")

# Modo de Tratamento de Dados
elif modo == "Data Processing":
    # Diretórios
    pasta_brutos = os.path.join(os.path.dirname(__file__), "dados_brutos")
    pasta_tratados = os.path.join(os.path.dirname(__file__), "dados_tratados")

    # Verifica se a pasta de dados tratados existe; caso contrário, cria a pasta
    if not os.path.exists(pasta_tratados):
        os.makedirs(pasta_tratados)

    # Lista os arquivos na pasta 'dados brutos'
    arquivos_brutos = os.listdir(pasta_brutos)

    # Lista os arquivos na pasta 'dados tratados'
    arquivos_tratados = os.listdir(pasta_tratados)

    # Exibe os arquivos que serão tratados
    st.write("Files to be processed:")
    if arquivos_brutos:
        st.write(arquivos_brutos)
    else:
        st.write("No files to process.")

    # Exibe os arquivos já tratados
    st.write("Files already processed:")
    if arquivos_tratados:
        st.write(arquivos_tratados)
    else:
        st.write("No files processed yet.")

    # Botão para iniciar o tratamento de dados
    if st.button("Start Processing"):
        for arquivo in arquivos_brutos:
            caminho_arquivo = os.path.join(pasta_brutos, arquivo)

            # Realiza o tratamento dos dados
            tratar_dados(caminho_arquivo, pasta_tratados)

        st.success("Data processed and saved in the 'processed data' folder!")

    # Permitir que o usuário baixe os arquivos já tratados
    st.write("Select the files you want to download:")

    arquivos_selecionados = st.multiselect("Select files", arquivos_tratados)

    for arquivo in arquivos_selecionados:
        caminho_arquivo = os.path.join(pasta_tratados, arquivo)
        with open(caminho_arquivo, "rb") as file:
            st.download_button(
                label=f"Download {arquivo}",
                data=file,
                file_name=arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Botão para baixar todos os arquivos não tratados (em dados_brutos)
    zip_buffer_brutos = io.BytesIO()
    with zipfile.ZipFile(zip_buffer_brutos, "w") as zip_file:
        for arquivo in arquivos_brutos:
            caminho_arquivo = os.path.join(pasta_brutos, arquivo)
            zip_file.write(caminho_arquivo, os.path.basename(caminho_arquivo))
    zip_buffer_brutos.seek(0)

    st.download_button(
        label="Download All Unprocessed Files (.zip)",
        data=zip_buffer_brutos,
        file_name="files_unprocessed.zip",
        mime="application/zip"
    )

    # Botão para baixar todos os arquivos tratados (em dados_tratados)
    zip_buffer_tratados = io.BytesIO()
    with zipfile.ZipFile(zip_buffer_tratados, "w") as zip_file:
        for arquivo in arquivos_tratados:
            caminho_arquivo = os.path.join(pasta_tratados, arquivo)
            zip_file.write(caminho_arquivo, os.path.basename(caminho_arquivo))
    zip_buffer_tratados.seek(0)

    st.download_button(
        label="Download All Processed Files (.zip)",
        data=zip_buffer_tratados,
        file_name="files_processed.zip",
        mime="application/zip"
    )

# Modo de Análise de Dados
elif modo == "Data Analysis":
    pasta_tratados = os.path.join(os.path.dirname(__file__), "dados_tratados")
    arquivo_saida_combinado = os.path.join(pasta_tratados, "dados_combinados.xlsx")
    arquivo_saida_filtrado = os.path.join(pasta_tratados, "dados_filtrados.xlsx")

    if st.button("Combine Data"):
        combinar_planilhas(pasta_tratados, arquivo_saida_combinado)
        st.success(f"Combined spreadsheet saved as '{arquivo_saida_combinado}'.")

    if os.path.exists(arquivo_saida_combinado):
        if st.button("Filter Data"):
            arquivo_saida_filtrado = filtrar_dados(arquivo_saida_combinado, pasta_tratados)
            st.success(f"Filtered spreadsheet saved as '{arquivo_saida_filtrado}'.")

    if os.path.exists(arquivo_saida_filtrado):
        st.header("Apartment Price Analysis")

        # Seleção de intervalo de quartos usando um único slider
        quartos_intervalo = st.slider('Select room range', 1, 10, (5, 6))

        # Seleção de intervalo de área usando um único slider
        area_intervalo = st.slider('Select area range (m²)', 10, 400, (150, 180))

        # Seleção de intervalo de preços usando um único slider
        preco_intervalo = st.slider('Select price range (CHF)', 0, 50000, (6000, 8000))

        # Seleção do tipo de transação
        tipos_transacao = ['Rent', 'Buy']
        tipo_selecionado = st.selectbox('Select transaction type', tipos_transacao)

        # Ler as cidades disponíveis no arquivo filtrado
        df_filtrado = pd.read_excel(arquivo_saida_filtrado)
        cidades_disponiveis = df_filtrado['City'].unique().tolist()

        # Adicionar uma seleção de múltiplas cidades
        cidades_selecionadas = st.multiselect('Select city(s)', cidades_disponiveis, default=cidades_disponiveis)

        if st.button("Plot Price Evolution"):
            plotar_evolucao_precos_e_mapa(
                arquivo_saida_filtrado,
                quartos_intervalo[0],
                quartos_intervalo[1],
                area_intervalo[0],
                area_intervalo[1],
                preco_intervalo[0],
                preco_intervalo[1],
                tipo_selecionado,
                cidades_selecionadas
            )