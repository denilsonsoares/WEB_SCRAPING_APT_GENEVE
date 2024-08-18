from datetime import datetime
import streamlit as st
import os
import pandas as pd
import zipfile
import io
import plotly.express as px
from utils_extract import raspar_dados, set_parar_raspagem, salvar_dados
from utils_treat import *
from utils_analytics import *

# Título do aplicativo
st.title("Web Scraping de Apartamentos")

# Seleção do modo: Raspagem, Tratamento de Dados ou Análise de Dados
modo = st.radio("Selecione o modo", ["Raspagem", "Tratamento de Dados", "Análise de Dados"])

# Modo de Raspagem
if modo == "Raspagem":
    # Seleção do site
    sites = st.multiselect("Selecione os sites", ["homegate", "immoscout24"], default=["homegate", "immoscout24"])

    # Seleção do tipo de transação
    tipos = st.multiselect("Tipos de transação", ["alugar", "comprar"], default=["alugar", "comprar"])

    # Seleção da cidade
    cidades = st.multiselect("Selecione as cidades", ["Geneve", "Zurich"], default=["Geneve", "Zurich"])

    # Botão para iniciar a raspagem
    iniciar_raspagem = st.button("Iniciar Raspagem")

    # Botão para parar a raspagem
    parar_raspagem = st.button("Parar Raspagem")

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
                    st.write(f"Iniciando a raspagem para {tipo} em {cidade} no site {site}...")

                    # Realiza a raspagem de dados
                    df = raspar_dados(site, tipo, cidade)
                    # Exibe os dados raspados
                    st.write(df)
                    st.success(f"Raspagem concluída para {site}, {tipo}, {cidade}!")

        if parar_raspagem:
            st.warning("Raspagem interrompida!")
        else:
            st.success("Raspagem concluída para todas as combinações!")

    if parar_raspagem:
        # Sinaliza para parar a raspagem
        set_parar_raspagem(True)
        st.warning("Raspagem interrompida!")

# Modo de Tratamento de Dados
elif modo == "Tratamento de Dados":
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
    st.write("Arquivos a serem tratados:")
    if arquivos_brutos:
        st.write(arquivos_brutos)
    else:
        st.write("Nenhum arquivo para tratar.")

    # Exibe os arquivos já tratados
    st.write("Arquivos já tratados:")
    if arquivos_tratados:
        st.write(arquivos_tratados)
    else:
        st.write("Nenhum arquivo tratado ainda.")

    # Botão para iniciar o tratamento de dados
    if st.button("Iniciar Tratamento"):
        for arquivo in arquivos_brutos:
            caminho_arquivo = os.path.join(pasta_brutos, arquivo)

            # Verifica o site e realiza o tratamento específico
            if "homegate" in arquivo:
                tratar_dados_homegate(caminho_arquivo, pasta_tratados)
            elif "immoscout24" in arquivo:
                tratar_dados_immoscout24(caminho_arquivo, pasta_tratados)

        st.success("Dados tratados e salvos na pasta 'dados tratados'!")

    # Permitir que o usuário baixe os arquivos já tratados
    st.write("Selecione os arquivos que deseja baixar:")

    arquivos_selecionados = st.multiselect("Selecione os arquivos", arquivos_tratados)

    for arquivo in arquivos_selecionados:
        caminho_arquivo = os.path.join(pasta_tratados, arquivo)
        with open(caminho_arquivo, "rb") as file:
            st.download_button(
                label=f"Baixar {arquivo}",
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
        label="Baixar Todos os Arquivos Não Tratados (.zip)",
        data=zip_buffer_brutos,
        file_name="arquivos_nao_tratados.zip",
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
        label="Baixar Todos os Arquivos Tratados (.zip)",
        data=zip_buffer_tratados,
        file_name="arquivos_tratados.zip",
        mime="application/zip"
    )

elif modo == "Análise de Dados":
    pasta_tratados = os.path.join(os.path.dirname(__file__), "dados_tratados")
    arquivo_saida = os.path.join(pasta_tratados, "dados_combinados.xlsx")
    arquivo_dados_filtrados = os.path.join(pasta_tratados, "dados_filtrados.xlsx")  # Caminho para os dados filtrados

    # Botão para combinar dados
    if st.button("Combinar Dados"):
        combinar_planilhas(pasta_tratados, arquivo_saida)
        st.success(f"Planilha combinada salva como '{arquivo_saida}'.")

    # Permitir que o usuário baixe o arquivo combinado
    if os.path.exists(arquivo_saida):
        with open(arquivo_saida, "rb") as file:
            st.download_button(
                label="Baixar Planilha Combinada",
                data=file,
                file_name="dados_combinados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # Carregar os dados combinados
    if os.path.exists(arquivo_saida):
        df_combined = carregar_dados_combinados(arquivo_saida)
        if df_combined is not None:
            df_valid = filtrar_apartamentos_validos(df_combined)

            cidade_selecionada = selecionar_cidade(df_valid)
            tipo_selecao = selecionar_tipo_transacao(df_valid)
            quartos_selecionados = selecionar_intervalo_quartos(df_valid)
            espaco_selecionado = selecionar_intervalo_espaco(df_valid)
            intervalo_preco = calcular_intervalo_preco(df_valid)
            intervalo_data = calcular_intervalo_data(df_valid)

            # Botão para filtrar dados
            if st.button("Filtrar Dados"):
                df_filtered = filtrar_dados(
                    df_valid,
                    cidade_selecionada,
                    tipo_selecao,
                    quartos_selecionados,
                    espaco_selecionado,
                    intervalo_preco[0],
                    intervalo_preco[1],
                    intervalo_data
                )

                # Salvar os dados filtrados em uma nova planilha
                caminho_filtrado = salvar_planilha_filtrada(df_filtered, arquivo_dados_filtrados)

            # Botão para mostrar gráficos de evolução dos preços
            if os.path.exists(arquivo_dados_filtrados):
                df_filtered = pd.read_excel(arquivo_dados_filtrados)
                if st.button("Mostrar Gráficos de Evolução de Preços"):
                    exibir_grafico_evolucao_precos(df_filtered)

            # Permitir que o usuário baixe os dados filtrados
            if os.path.exists(arquivo_dados_filtrados):
                with open(arquivo_dados_filtrados, "rb") as file:
                    st.download_button(
                        label="Baixar Dados Filtrados",
                        data=file,
                        file_name="dados_filtrados.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )