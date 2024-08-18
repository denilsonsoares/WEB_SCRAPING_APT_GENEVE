import pandas as pd
import re
import os

def obter_cidade_do_arquivo(file_path):
    """Obtém a cidade a partir do nome do arquivo."""
    if 'geneve' in file_path.lower():
        return 'Geneve'
    elif 'zurich' in file_path.lower():
        return 'Zurich'
    else:
        return 'Unknown'

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

    # Função para extrair valor numérico do aluguel, mantendo "N/A" quando presente
    def extract_numeric_rent(rent):
        if pd.isna(rent) or isinstance(rent, str) and ('N/A' in rent or 'Price on request' in rent):
            return 'N/A'
        return re.sub(r'[^\d,]', '', rent)

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

    # Função para remover as vírgulas dos valores
    def format_brazilian_rent(rent):
        if rent == 'N/A':
            return rent
        return rent.replace(',', '')

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(format_brazilian_rent)

    # Função para formatar o campo 'Rooms'
    def format_rooms(rooms):
        if pd.isna(rooms):
            return 'N/A'
        if isinstance(rooms, str) and 'N/A' in rooms:
            return 'N/A'
        return re.sub(r'\s*room\(s\)', '', str(rooms)).strip()

    df['Rooms'] = df['Rooms'].apply(format_rooms)

    # Função para extrair apenas números da área, preservando "N/A"
    def extract_numeric_space(space):
        if pd.isna(space) or isinstance(space, str) and 'N/A' in space:
            return 'N/A'
        return re.sub(r'\D', '', str(space)).strip()

    df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

    # Obter cidade a partir do nome do arquivo
    df['City'] = obter_cidade_do_arquivo(file_path)
    df['Country'] = 'Switzerland'

    # Verificar se é aluguel ou compra
    if "comprar" in file_path:
        df.rename(columns={'Rent (CHF)': 'Price (CHF)'}, inplace=True)

    # Definir a ordem das colunas
    columns_order = ['Title', 'Rent (CHF)', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    data = file_path.split("_")[-1].split(".")[0]
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(os.path.basename(file_path))[0]}_updated.xlsx")
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

    # Função para extrair valor numérico do aluguel, mantendo "N/A" ou "Price on request" quando presente
    def extract_numeric_rent(rent):
        if pd.isna(rent) or isinstance(rent, str) and ('N/A' in rent or 'Price on request' in rent):
            return 'N/A'
        return re.sub(r'[^\d,]', '', rent)

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

    # Função para remover as vírgulas dos valores
    def format_brazilian_rent(rent):
        if rent == 'N/A':
            return rent
        return rent.replace(',', '')

    df['Rent (CHF)'] = df['Rent (CHF)'].apply(format_brazilian_rent)

    # Função para formatar o campo 'Rooms'
    def format_rooms(rooms):
        if pd.isna(rooms):
            return 'N/A'
        if isinstance(rooms, str) and 'N/A' in rooms:
            return 'N/A'
        return re.sub(r'\s*rooms?', '', str(rooms)).strip()

    df['Rooms'] = df['Rooms'].apply(format_rooms)

    # Função para extrair apenas números da área, preservando "N/A"
    def extract_numeric_space(space):
        if pd.isna(space) or isinstance(space, str) and 'N/A' in space:
            return 'N/A'
        return re.sub(r'\D', '', str(space)).strip()

    df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

    # Obter cidade a partir do nome do arquivo
    df['City'] = obter_cidade_do_arquivo(file_path)
    df['Country'] = 'Switzerland'

    # Verificar se é aluguel ou compra
    if "comprar" in file_path:
        df.rename(columns={'Rent (CHF)': 'Price (CHF)'}, inplace=True)

    # Definir a ordem das colunas
    columns_order = ['Title', 'Rent (CHF)', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    data = file_path.split("_")[-1].split(".")[0]
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(os.path.basename(file_path))[0]}_updated.xlsx")
    df.to_excel(new_file_path, index=False)

    print(f"Planilha '{file_path}' tratada e salva como '{new_file_path}'.")
