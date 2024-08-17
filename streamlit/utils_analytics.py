# utils_analytics.py
import pandas as pd
import re
import os

def extrair_id(link):
    """Extrai o ID do link fornecido."""
    match = re.search(r'/(\d+)$', link)
    return match.group(1) if match else None

def combinar_planilhas(pasta_tratados, arquivo_saida):
    """Combina todas as planilhas na pasta especificada em uma única planilha e agrupa por ID."""
    arquivos = [f for f in os.listdir(pasta_tratados) if f.endswith('.xlsx')]
    df_list = []

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta_tratados, arquivo)
        df = pd.read_excel(caminho_arquivo)

        # Adicionar coluna Type of Transaction com base no nome do arquivo
        tipo_transacao = 'Rent' if 'alugar' in arquivo else 'Buy'
        df['Type of Transaction'] = tipo_transacao

        # Adicionar coluna ID extraído do link
        df['ID'] = df['Extracted from'].apply(extrair_id)

        df_list.append(df)

    df_combined = pd.concat(df_list, ignore_index=True)

    # Agrupar os dados por ID
    grouped = df_combined.groupby('ID').agg({
        'Title': 'first',
        'Address': 'first',
        'City': 'first',
        'Country': 'first',
        'Type of Transaction': 'first',
        'Extracted from': 'first',
        'Data extracted when': lambda x: list(x),
        'Rent (CHF)': lambda x: list(x),
        'Price (CHF)': lambda x: list(x),
        'Rooms': 'first'  # Mantém a coluna 'Rooms'
    }).reset_index()

    # Criar coluna com lista de preços e datas
    grouped['Price and Date'] = grouped.apply(
        lambda row: list(zip(row['Price (CHF)'], row['Data extracted when'])), axis=1)

    # Remover colunas desnecessárias
    grouped = grouped.drop(columns=['Rent (CHF)', 'Price (CHF)'])

    # Salvar a planilha combinada
    grouped.to_excel(arquivo_saida, index=False)
    print(f"Planilha combinada salva como '{arquivo_saida}'.")
