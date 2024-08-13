import pandas as pd
import re

# Carregar a planilha Excel
file_path = 'immoscout_geneva_total.xlsx'
df = pd.read_excel(file_path)

# Renomear as colunas para inglês
df.rename(columns={
    'Título': 'Title',
    'Aluguel': 'Rent (CHF)',
    'Quartos': 'Rooms',
    'Espaço': 'Living Space (m²)',
    'Endereço': 'Address',
}, inplace=True)

# Função para extrair valor numérico do aluguel, preservando a formatação
def extract_numeric_rent(rent):
    if isinstance(rent, str) and 'On request' in rent:
        return rent
    else:
        # Preservar os separadores de milhar e remover o restante
        return re.sub(r'[^\d,]', '', rent)

df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

# Função para formatar o campo 'Rooms'
def format_rooms(rooms):
    # Remove as palavras "room" ou "rooms" e mantém o número
    return re.sub(r'\s*rooms?', '', rooms).strip()

df['Rooms'] = df['Rooms'].apply(format_rooms)

# Função para extrair apenas números da área, preservando "N/A"
def extract_numeric_space(space):
    if re.match(r'^\d+\s*m²$', space):
        # Remove "m²" se o formato for "40 m²" ou "40m²"
        return re.sub(r'\s*m²$', '', space).strip()
    else:
        # Caso contrário, deixe o valor como está
        return space

df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

# Adicionar colunas para cidade e país
df['City'] = 'Genève'
df['Country'] = 'Switzerland'

# Definir a ordem das colunas
columns_order = ['Title', 'Rent (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country']
df = df.reindex(columns=columns_order)

# Salvar a nova planilha
new_file_path = 'immoscout_geneva_total_updated.xlsx'
df.to_excel(new_file_path, index=False)

print(f"Planilha atualizada e salva como '{new_file_path}'.")
