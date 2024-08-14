import pandas as pd
import re

# Carregar a planilha Excel
file_path = 'buy_homegate_zurich.xlsx'
df = pd.read_excel(file_path)

# Renomear as colunas para inglês
df.rename(columns={
    'Título': 'Title',
    'Aluguel': 'Price (CHF)',
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
        # Preservar os separadores de milhar e remover o restante
        return re.sub(r'[^\d,]', '', rent)

df['Price (CHF)'] = df['Price (CHF)'].apply(extract_numeric_rent)

# Função para remover as vírgulas dos valores
def format_brazilian_rent(rent):
    if isinstance(rent, str):
        return rent.replace(',', '')
    return rent

df['Price (CHF)'] = df['Price (CHF)'].apply(format_brazilian_rent)

# Função para formatar o campo 'Rooms'
def format_rooms(rooms):
    # Remove a palavra "room(s)" e mantém apenas o número
    return re.sub(r'\s*room\(s\)', '', rooms).strip()

df['Rooms'] = df['Rooms'].apply(format_rooms)

# Função para extrair apenas números da área, removendo "m²"
def extract_numeric_space(space):
    # Remove tudo que não for número ou espaço
    return re.sub(r'\D', '', space).strip()

df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

# Adicionar colunas para cidade e país
df['City'] = 'Zurich'
df['Country'] = 'Switzerland'

# Definir a ordem das colunas
columns_order = ['Title', 'Price (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
df = df.reindex(columns=columns_order)

# Salvar a nova planilha
new_file_path = 'buy_homegate_zurich_updated.xlsx'
df.to_excel(new_file_path, index=False)

print(f"Planilha atualizada e salva como '{new_file_path}'.")
