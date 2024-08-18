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

                    # Salva os dados raspados em um arquivo Excel
                    #data_extracao = datetime.now().strftime('%Y%m%d')
                    #nome_arquivo = f"{site}_{tipo}_{cidade.lower()}_{data_extracao}.xlsx"
                    #pasta_dados_brutos = "dados_brutos"
                    #os.makedirs(pasta_dados_brutos, exist_ok=True)
                    #salvar_dados(df, pasta_dados_brutos, nome_arquivo)

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

# Modo de Análise de Dados
elif modo == "Análise de Dados":
    pasta_tratados = os.path.join(os.path.dirname(__file__), "dados_tratados")
    arquivo_saida = os.path.join(pasta_tratados, "dados_combinados.xlsx")

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
        df_combined = pd.read_excel(arquivo_saida)

        # Seletor de cidade
        cidades = df_combined['City'].unique()
        cidade_selecionada = st.selectbox("Selecione a cidade", cidades)

        # Seletor de tipo de transação
        tipos = df_combined['Type of Transaction'].unique()
        tipo_selecao = st.selectbox("Selecione o tipo de transação", tipos)

        # Seletor de quantidade de quartos
        quartos_opcoes = df_combined['Rooms'].unique()
        quartos_opcoes = [str(q) for q in quartos_opcoes if pd.notna(q)]
        quartos_opcoes = sorted(set(quartos_opcoes))
        quartos_opcoes.append("Todos")
        quartos_selecionados = st.selectbox("Selecione a quantidade de quartos", quartos_opcoes)

        # Intervalo de preço
        min_preco = df_combined['Price and Date'].apply(
            lambda x: min([float(p[0]) for p in x if isinstance(p, tuple) and len(p) == 2] if x else [0])
        ).min()

        max_preco = df_combined['Price and Date'].apply(
            lambda x: max([float(p[0]) for p in x if isinstance(p, tuple) and len(p) == 2] if x else [0])
        ).max()

        intervalo_preco = st.slider("Intervalo de preço", min_value=float(min_preco), max_value=float(max_preco), value=(float(min_preco), float(max_preco)))

        # Filtrar dados com base nas seleções
        df_filtrado = df_combined[
            (df_combined['City'] == cidade_selecionada) &
            (df_combined['Type of Transaction'] == tipo_selecao)
        ]

        if quartos_selecionados != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Rooms'] == float(quartos_selecionados)]

        df_filtrado = df_filtrado[df_filtrado['Price and Date'].apply(lambda x: any(float(p) >= intervalo_preco[0] and float(p) <= intervalo_preco[1] for p, _ in x))]

        # Exibir dados filtrados
        st.write("Dados Filtrados:")
        st.write(df_filtrado)

        # Verifica se há dados para plotar
        if not df_filtrado.empty:
            # Preparar os dados para plotar
            df_long = df_filtrado.explode('Price and Date')
            df_long[['Price', 'Date']] = pd.DataFrame(df_long['Price and Date'].tolist(), index=df_long.index)

            # Converter a coluna de datas para o tipo datetime
            df_long['Date'] = pd.to_datetime(df_long['Date'], format='%d-%m-%Y')

            # Ordenar por data
            df_long = df_long.sort_values('Date')

            # Gráfico de linha para mostrar a evolução dos preços ao longo do tempo
            fig = px.line(df_long, x='Date', y='Price', title="Evolução dos Preços ao Longo do Tempo")
            st.plotly_chart(fig)

            # Gráfico de boxplot para distribuição de preços por quantidade de quartos
            fig2 = px.box(df_long, x='Rooms', y='Price', title="Distribuição de Preços por Quartos")
            st.plotly_chart(fig2)

            st.write(f"Total de imóveis encontrados: {len(df_filtrado)}")