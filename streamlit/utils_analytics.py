#utils_analytics.py
import re
import os
import pandas as pd
from datetime import datetime
import streamlit as st
import plotly.express as px
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

    # Remove duplicatas mantendo o primeiro preço com a data
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

        # Adicionar colunas com base no nome do arquivo
        partes_nome = os.path.splitext(arquivo)[0].split('_')
        site, tipo_transacao, cidade = partes_nome[0], partes_nome[1], partes_nome[2]

        df['Type of Transaction'] = 'Rent' if 'alugar' in tipo_transacao else 'Buy'
        df['City'] = cidade.capitalize()
        df['Country'] = 'Switzerland'
        df['Source'] = site

        # Adicionar coluna ID extraído do link
        df['ID'] = df['Extracted from'].apply(extrair_id)

        # Unificar as colunas de preço
        df['Price (CHF)'] = df['Price (CHF)'].combine_first(df['Price (CHF)'])

        df_list.append(df)

    df_combined = pd.concat(df_list, ignore_index=True)

    # Substituir os valores 'N/A' com o primeiro valor válido antes de agrupar por ID
    df_combined['Title'] = df_combined.groupby('ID')['Title'].transform(obter_primeiro_valor_valido)
    df_combined['Address'] = df_combined.groupby('ID')['Address'].transform(obter_primeiro_valor_valido)
    df_combined['Rooms'] = df_combined.groupby('ID')['Rooms'].transform(obter_primeiro_valor_valido)
    df_combined['Living Space (m²)'] = df_combined.groupby('ID')['Living Space (m²)'].transform(obter_primeiro_valor_valido)

    # Agrupar os dados por ID
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

    # Criar coluna com lista de preços e datas, e processar os dados
    grouped['Price and Date'] = grouped.apply(
        lambda row: processar_preco_data(list(zip(row['Price (CHF)'], row['Data extracted when']))), axis=1)

    # Remover colunas desnecessárias, incluindo 'Price (CHF)' e 'Data extracted when'
    grouped = grouped.drop(columns=['Price (CHF)', 'Data extracted when'])

    # Salvar a planilha combinada
    grouped.to_excel(arquivo_saida, index=False)
    print(f"Planilha combinada salva como '{arquivo_saida}'.")


def carregar_dados_combinados(arquivo_saida):
    if os.path.exists(arquivo_saida):
        return pd.read_excel(arquivo_saida)
    return None

def filtrar_apartamentos_validos(df_combined):
    # Filtra apartamentos com valores válidos para Rooms e Living Space (m²)
    return df_combined[(df_combined['Rooms'].notna()) & (df_combined['Living Space (m²)'].notna())]

def selecionar_cidade(df_valid):
    cidades = df_valid['City'].unique()
    return st.selectbox("Selecione a cidade", cidades)

def selecionar_tipo_transacao(df_valid):
    tipos = df_valid['Type of Transaction'].unique()
    return st.selectbox("Selecione o tipo de transação", tipos)

def selecionar_intervalo_quartos(df_valid):
    quartos_min = int(df_valid['Rooms'].min())
    quartos_max = int(df_valid['Rooms'].max())
    return st.slider("Selecione o intervalo de quantidade de quartos", min_value=quartos_min, max_value=quartos_max, value=(quartos_min, quartos_max))

def selecionar_intervalo_espaco(df_valid):
    espaco_min = int(df_valid['Living Space (m²)'].min())
    espaco_max = int(df_valid['Living Space (m²)'].max())
    return st.slider("Selecione o intervalo de Living Space (m²)", min_value=espaco_min, max_value=espaco_max, value=(espaco_min, espaco_max))

def calcular_intervalo_preco(df_valid):
    # Extrai os preços válidos de cada entrada na coluna 'Price and Date'
    precos = df_valid['Price and Date'].apply(
        lambda x: [p[0] for p in eval(x) if isinstance(p, tuple) and len(p) == 2]
    ).explode()

    # Remove valores NaN e converte para float
    precos = precos.dropna().astype(float)

    # Verifica se há preços disponíveis para calcular os intervalos
    if not precos.empty:
        preco_min = precos.min()
        preco_max = precos.max()
        return st.slider("Intervalo de preço", min_value=preco_min, max_value=preco_max, value=(preco_min, preco_max))
    else:
        st.warning("Não há preços válidos disponíveis para cálculo.")
        return (0, 0)



def calcular_intervalo_data(df_valid):
    data_min = df_valid['Price and Date'].apply(lambda x: min([datetime.strptime(p[1], '%d-%m-%Y') for p in x if isinstance(p, tuple) and len(p) == 2]) if x else None).dropna().min()
    data_max = df_valid['Price and Date'].apply(lambda x: max([datetime.strptime(p[1], '%d-%m-%Y') for p in x if isinstance(p, tuple) and len(p) == 2]) if x else None).dropna().max()
    return st.slider("Intervalo de datas", min_value=data_min, max_value=data_max, value=(data_min, data_max))

def filtrar_dados(df_valid, cidade_selecionada, tipo_selecao, quartos_selecionados, espaco_selecionado, preco_min, preco_max, intervalo_data):
    return df_valid[
        (df_valid['City'] == cidade_selecionada) &
        (df_valid['Type of Transaction'] == tipo_selecao) &
        (df_valid['Rooms'].between(quartos_selecionados[0], quartos_selecionados[1])) &
        (df_valid['Living Space (m²)'].between(espaco_selecionado[0], espaco_selecionado[1])) &
        (df_valid['Price and Date'].apply(lambda x: any(
            preco_min <= p[0] <= preco_max and intervalo_data[0] <= datetime.strptime(p[1], '%d-%m-%Y') <= intervalo_data[1]
            for p in x if isinstance(p, tuple) and len(p) == 2)))
    ]

def exibir_grafico_interativo(df_filtered):
    fig = px.scatter(df_filtered, x="Price", y="Rooms", color="City", size="Size",
                     hover_data=['City', 'Price', 'Rooms', 'Size'])
    st.plotly_chart(fig)