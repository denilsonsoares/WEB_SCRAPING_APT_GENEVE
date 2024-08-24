import pandas as pd
import re
import os

def tratar_dados_homegate(file_path, pasta_tratados):
    df = pd.read_excel(file_path)

    # Renomear as colunas para inglês
    df.rename(columns={
        'Título': 'Title',
        'Preço (CHF)': 'Price (CHF)',  # Renomeado para "Price (CHF)"
        'Quartos': 'Rooms',
        'Espaço': 'Living Space (m²)',
        'Endereço': 'Address',
        'Link': 'Extracted from',
        'Data': 'Data extracted when',
    }, inplace=True)

    # Função para extrair valor numérico do preço, mantendo "N/A" quando presente
    def extract_numeric_price(price):
        if pd.isna(price) or isinstance(price, str) and ('N/A' in price or 'Price on request' in price):
            return 'N/A'
        return re.sub(r'[^\d,]', '', price)

    df['Price (CHF)'] = df['Price (CHF)'].apply(extract_numeric_price)

    # Função para remover as vírgulas dos valores
    def format_brazilian_price(price):
        if price == 'N/A':
            return price
        return price.replace(',', '')

    df['Price (CHF)'] = df['Price (CHF)'].apply(format_brazilian_price)

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

    # Extrair cidade e tipo de transação do nome do arquivo
    file_name = os.path.basename(file_path)
    city = 'Geneve' if 'geneve' in file_name.lower() else 'Zurich'
    transaction_type = 'Rent' if 'alugar' in file_name.lower() else 'Buy'

    # Adicionar colunas para cidade, país e tipo de transação
    df['City'] = city
    df['Country'] = 'Switzerland'
    df['Type of Transaction'] = transaction_type

    # Definir a ordem das colunas
    columns_order = ['Title', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when', 'Type of Transaction']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(file_name)[0]}_updated.xlsx")
    df.to_excel(new_file_path, index=False)

    print(f"Planilha '{file_path}' tratada e salva como '{new_file_path}'.")

def tratar_dados_immoscout24(file_path, pasta_tratados):
    df = pd.read_excel(file_path)

    # Renomear as colunas para inglês
    df.rename(columns={
        'Título': 'Title',
        'Preço (CHF)': 'Price (CHF)',  # Renomeado para "Price (CHF)"
        'Quartos': 'Rooms',
        'Espaço': 'Living Space (m²)',
        'Endereço': 'Address',
        'Link': 'Extracted from',
        'Data': 'Data extracted when',
    }, inplace=True)

    # Função para extrair valor numérico do preço, mantendo "N/A" ou "Price on request" quando presente
    def extract_numeric_price(price):
        if pd.isna(price) or isinstance(price, str) and ('N/A' in price or 'Price on request' in price):
            return 'N/A'
        return re.sub(r'[^\d,]', '', price)

    df['Price (CHF)'] = df['Price (CHF)'].apply(extract_numeric_price)

    # Função para remover as vírgulas dos valores
    def format_brazilian_price(price):
        if price == 'N/A':
            return price
        return price.replace(',', '')

    df['Price (CHF)'] = df['Price (CHF)'].apply(format_brazilian_price)

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

    # Extrair cidade e tipo de transação do nome do arquivo
    file_name = os.path.basename(file_path)
    city = 'Geneve' if 'geneve' in file_name.lower() else 'Zurich'
    transaction_type = 'Rent' if 'alugar' in file_name.lower() else 'Buy'

    # Adicionar colunas para cidade, país e tipo de transação
    df['City'] = city
    df['Country'] = 'Switzerland'
    df['Type of Transaction'] = transaction_type

    # Definir a ordem das colunas
    columns_order = ['Title', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when', 'Type of Transaction']
    df = df.reindex(columns=[col for col in columns_order if col in df.columns])

    # Salvar a nova planilha
    new_file_path = os.path.join(pasta_tratados, f"{os.path.splitext(file_name)[0]}_updated.xlsx")
    df.to_excel(new_file_path, index=False)

    print(f"Planilha '{file_path}' tratada e salva como '{new_file_path}'.")
