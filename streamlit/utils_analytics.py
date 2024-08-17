import pandas as pd
import os
import re


def extrair_id(link):
    match = re.search(r'(\d+)', link)
    return match.group(1) if match else None


def analisar_variacao_precos(tipo_transacao, cidade, faixa_preco, num_quartos):
    pasta_tratados = os.path.join(os.path.dirname(__file__), "dados_tratados")
    arquivos = [os.path.join(pasta_tratados, f) for f in os.listdir(pasta_tratados) if f.endswith("_updated.xlsx")]

    dfs = []
    for arquivo in arquivos:
        df = pd.read_excel(arquivo)

        # Aplicar filtros
        df = df[(df['City'] == cidade) &
                (df['Rent (CHF)'].apply(
                    lambda x: faixa_preco[0] <= float(x) <= faixa_preco[1] if x != 'N/A' else False)) &
                (df['Rooms'].apply(lambda x: num_quartos[0] <= float(x) <= num_quartos[1] if x != 'N/A' else False))]

        df['Apartment ID'] = df['Extracted from'].apply(extrair_id)
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df_final = pd.concat(dfs)
    df_final['Data extracted when'] = pd.to_datetime(df_final['Data extracted when'])

    # Pivotar os dados para a análise temporal
    df_pivot = df_final.pivot_table(index='Data extracted when', columns='Apartment ID', values='Rent (CHF)',
                                    aggfunc='mean')

    return df_pivot
