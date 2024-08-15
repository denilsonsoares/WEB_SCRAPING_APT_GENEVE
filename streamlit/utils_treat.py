# utils_treat.py
import pandas as pd
import re
import os

def tratar_dados_homegate(file_path, pasta_tratados):
    df = pd.read_excel(file_path)

    # Renomear as colunas para inglês
    df.rename(columns={
        'Título': 'Title',
        'Aluguel': 'Rent (CHF)',
        'Quartos': 'Rooms',
        'Espaço': 'Living Space (m²)',
        'Endereço': 'Address',
        'Link': 'Extracted from',
        'Data': 'Data extracted when',
    }, inplace=True)

    # Função para extrair valor numérico do aluguel
    def extract_numeric_rent(rent):
        if isinstance(rent, str) and 'Price on request' in rent:
            return rent
        else:
            return re.sub(r'[^\d,]', '', rent)

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

    # Função para remover as vírgulas dos valores
    def format_brazilian_rent(rent):
        if isinstance(rent, str):
            return rent.replace(',', '')
        return rent

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(format_brazilian_rent)

    # Função para formatar o campo 'Rooms'
    def format_rooms(rooms):
        return re.sub(r'\s*room\(s\)', '', rooms).strip()

    df['Rooms'] = df['Rooms'].apply(format_rooms)

    # Função para extrair apenas números da área, preservando "N/A"
    def extract_numeric_space(space):
        if isinstance(space, str):
            return re.sub(r'\D', '', space).strip()
        elif pd.isna(space):
            return 'N/A'
        else:
            return str(space)

    df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

    # Adicionar colunas para cidade e país
    df['City'] = 'Genève'
    df['Country'] = 'Switzerland'

    # Verificar se é aluguel ou compra
    if "comprar" in file_path:
        df.rename(columns={'Rent (CHF)': 'Price (CHF)'}, inplace=True)

    # Definir a ordem das colunas
    columns_order = ['Title', 'Rent (CHF)', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    data = file_path.split("_")[-1].split(".")[0]
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(os.path.basename(file_path))[0]}_updated_{data}.xlsx")
    df.to_excel(new_file_path, index=False)

    print(f"Planilha '{file_path}' tratada e salva como '{new_file_path}'.")


def tratar_dados_immoscout24(file_path, pasta_tratados):
    df = pd.read_excel(file_path)

    # Renomear as colunas para inglês
    df.rename(columns={
        'Título': 'Title',
        'Aluguel': 'Rent (CHF)',
        'Quartos': 'Rooms',
        'Espaço': 'Living Space (m²)',
        'Endereço': 'Address',
        'Link': 'Extracted from',
        'Data': 'Data extracted when',
    }, inplace=True)

    # Função para extrair valor numérico do aluguel, mantendo "On request" quando presente
    def extract_numeric_rent(rent):
        if isinstance(rent, str) and 'Price on request' in rent:
            return rent
        else:
            return re.sub(r'[^\d,]', '', rent)

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

    # Função para remover as vírgulas dos valores
    def format_brazilian_rent(rent):
        if isinstance(rent, str):
            return rent.replace(',', '')
        return rent

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(format_brazilian_rent)

    # Função para formatar o campo 'Rooms'
    def format_rooms(rooms):
        if isinstance(rooms, str):
            return re.sub(r'\s*rooms?', '', rooms).strip()
        elif pd.isna(rooms):
            return 'N/A'
        return str(rooms)

    df['Rooms'] = df['Rooms'].apply(format_rooms)

    # Função para extrair apenas números da área, preservando "N/A"
    def extract_numeric_space(space):
        if isinstance(space, str) and 'N/A' in space:
            return space
        elif pd.isna(space):
            return 'N/A'
        else:
            return str(re.sub(r'\D', '', space).strip())

    df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

    # Adicionar colunas para cidade e país
    df['City'] = 'Genève'
    df['Country'] = 'Switzerland'

    # Verificar se é aluguel ou compra
    if "comprar" in file_path:
        df.rename(columns={'Rent (CHF)': 'Price (CHF)'}, inplace=True)

    # Definir a ordem das colunas
    columns_order = ['Title', 'Rent (CHF)', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    data = file_path.split("_")[-1].split(".")[0]
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(os.path.basename(file_path))[0]}_updated_{data}.xlsx")
    df.to_excel(new_file_path, index=False)

    print(f"Planilha '{file_path}' tratada e salva como '{new_file_path}'.")
