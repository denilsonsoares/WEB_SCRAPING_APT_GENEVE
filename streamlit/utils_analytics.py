import re
import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def extrair_id(link):
    """Extrai o ID do link fornecido."""
    match = re.search(r'/(\d+)$', link)
    return match.group(1) if match else None

def processar_preco_data(lista_precos_datas):
    """Processa a lista de preços e datas, removendo nan, formatando datas e removendo duplicatas."""
    lista_processada = [
        (preco, pd.to_datetime(data).strftime('%Y-%d-%m'))
        for preco, data in lista_precos_datas
        if pd.notna(preco) and pd.notna(data)
    ]
    lista_processada = list(dict.fromkeys(lista_processada))
    return lista_processada

def obter_primeiro_valor_valido(values):
    """Retorna o primeiro valor válido (não N/A) de uma série de valores."""
    for value in values:
        if pd.notna(value) and value != 'N/A':
            return value
    return 'N/A'

def combinar_planilhas(pasta_tratados, arquivo_saida):
    """Combina todas as planilhas na pasta especificada em uma única planilha e agrupa por ID."""
    arquivos = [f for f in os.listdir(pasta_tratados) if f.endswith('_updated.xlsx')]
    df_list = []

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta_tratados, arquivo)
        df = pd.read_excel(caminho_arquivo)

        partes_nome = os.path.splitext(arquivo)[0].split('_')
        site, tipo_transacao, cidade = partes_nome[0], partes_nome[1], partes_nome[2]

        df['Type of Transaction'] = 'Rent' if 'alugar' in tipo_transacao else 'Buy'
        df['City'] = cidade.capitalize()
        df['Country'] = 'Switzerland'
        df['Source'] = site
        df['ID'] = df['Extracted from'].apply(extrair_id)

        df['Price (CHF)'] = df['Price (CHF)'].combine_first(df['Price (CHF)'])
        df_list.append(df)

    df_combined = pd.concat(df_list, ignore_index=True)
    df_combined['Title'] = df_combined.groupby('ID')['Title'].transform(obter_primeiro_valor_valido)
    df_combined['Address'] = df_combined.groupby('ID')['Address'].transform(obter_primeiro_valor_valido)
    df_combined['Rooms'] = df_combined.groupby('ID')['Rooms'].transform(obter_primeiro_valor_valido)
    df_combined['Living Space (m²)'] = df_combined.groupby('ID')['Living Space (m²)'].transform(obter_primeiro_valor_valido)

    grouped = df_combined.groupby('ID').agg({
        'Title': 'first',
        'Address': 'first',
        'City': 'first',
        'Country': 'first',
        'Type of Transaction': 'first',
        'Source': 'first',
        'Extracted from': 'first',
        'Data extracted when': lambda x: list(x),
        'Price (CHF)': lambda x: list(x),
        'Rooms': 'first',
        'Living Space (m²)': 'first'
    }).reset_index()

    grouped['Price and Date'] = grouped.apply(
        lambda row: processar_preco_data(list(zip(row['Price (CHF)'], row['Data extracted when']))), axis=1)

    grouped = grouped.drop(columns=['Price (CHF)', 'Data extracted when'])
    grouped.to_excel(arquivo_saida, index=False)
    print(f"Planilha combinada salva como '{arquivo_saida}'.")

def filtrar_dados(arquivo_entrada, pasta_saida):
    # Ler o arquivo combinado em um dataframe
    df = pd.read_excel(arquivo_entrada)

    # Remover linhas com qualquer valor N/A ou vazio em qualquer coluna
    df = df.dropna()

    # Filtrar a coluna "Price and Date" para remover tuplas vazias
    df = df[df["Price and Date"].apply(lambda x: len(x) > 0)]

    # Salvar o dataframe filtrado em um novo arquivo Excel
    arquivo_saida = os.path.join(pasta_saida, "dados_filtrados.xlsx")
    df.to_excel(arquivo_saida, index=False)

    return arquivo_saida

def plotar_evolucao_precos(arquivo_entrada, min_quartos, max_quartos, min_area, max_area):
    # Ler o arquivo filtrado em um dataframe
    df = pd.read_excel(arquivo_entrada)

    # Filtrar os dados com base no número de quartos e na área
    df_filtrado = df[(df['Rooms'].between(min_quartos, max_quartos)) &
                     (df['Living Space (m²)'].between(min_area, max_area))]

    # Aumentar a largura da imagem ajustando o figsize
    plt.figure(figsize=(14, 6))  # Aumentei a largura para 14 polegadas e mantive a altura em 6 polegadas

    for index, row in df_filtrado.iterrows():
        price_dates = eval(row['Price and Date'])  # Converte a string de volta para uma lista de tuplas

        if len(price_dates) > 0:  # Verifica se a lista não está vazia
            prices, dates = zip(*price_dates)

            # Convertendo as datas para o formato datetime para plotagem
            dates = pd.to_datetime(dates, format='%Y-%d-%m')

            # Plotar com pontos maiores
            plt.plot(dates, prices, marker='o', markersize=8, label=f'Apt {index + 1}')

    plt.xlabel('Data')
    plt.ylabel('Preço')
    plt.title('Evolução dos Preços dos Apartamentos')
    plt.legend()
    plt.grid(True)

    # Usar st.pyplot para exibir o gráfico no Streamlit
    st.pyplot(plt)

    # Exibir a tabela de apartamentos abaixo do gráfico
    # Criar a coluna de links clicáveis
    df_filtrado['Link'] = df_filtrado['Extracted from'].apply(
        lambda x: f'<a href="{x}" target="_blank">Visitar Apartamento</a>')

    # Selecionar colunas para exibir
    colunas_exibir = ['Rooms', 'Living Space (m²)', 'Price and Date', 'Link']

    # Exibir o dataframe como HTML
    st.markdown(df_filtrado[colunas_exibir].to_html(escape=False, index=False), unsafe_allow_html=True)