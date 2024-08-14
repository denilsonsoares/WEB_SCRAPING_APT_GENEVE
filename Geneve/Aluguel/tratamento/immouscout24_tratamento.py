import pandas as pd
import re

# Carregar a planilha Excel
file_path = 'rent_immoscout_geneve.xlsx'
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
        # Preservar os separadores de milhar e remover o restante
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
        # Remove as palavras "room" ou "rooms" e mantém o número
        return re.sub(r'\s*rooms?', '', rooms).strip()
    elif pd.isna(rooms):  # Verifica se o valor é NaN
        return 'N/A'
    return str(rooms)  # Retorna o valor original convertido para string

df['Rooms'] = df['Rooms'].apply(format_rooms)

# Função para extrair apenas números da área, preservando "N/A"
def extract_numeric_space(space):
    if isinstance(space, str) and 'N/A' in space:
        return space
    elif pd.isna(space):  # Verifica se o valor é NaN
        return 'N/A'
    else:
        return re.sub(r'\D', '', space).strip()

df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

# Adicionar colunas para cidade e país
df['City'] = 'Genève'
df['Country'] = 'Switzerland'

# Definir a ordem das colunas
columns_order = ['Title', 'Rent (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country', 'Extracted from', 'Data extracted when']
df = df.reindex(columns=columns_order)

# Salvar a nova planilha
new_file_path = 'rent_immoscout_geneve_updated.xlsx'
df.to_excel(new_file_path, index=False)

print(f"Planilha atualizada e salva como '{new_file_path}'.")
