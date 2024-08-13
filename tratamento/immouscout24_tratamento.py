import pandas as pd
import re

# Carregar a planilha Excel
file_path = 'apartamentos_geneva.xlsx'
df = pd.read_excel(file_path)

# Renomear as colunas para inglês
df.rename(columns={
    'Título': 'Title',
    'Aluguel': 'Rent (CHF)',
    'Quartos': 'Rooms',
    'Espaço': 'Living Space (m²)',
    'Endereço': 'Address',
    'Link': 'Link'
}, inplace=True)

# Função para extrair valor numérico do aluguel, preservando a formatação
def extract_numeric_rent(rent):
    if isinstance(rent, str) and 'On request' in rent:
        return rent
    else:
        # Preservar os separadores de milhar e remover o restante
        return re.sub(r'[^\d,]', '', rent)

df['Rent (CHF)'] = df['Rent (CHF)'].apply(extract_numeric_rent)

# Função para extrair apenas números da área, preservando "N/A"
def extract_numeric_space(space):
    if isinstance(space, float) and pd.isna(space):
        return space  # Preserva valores NaN
    elif isinstance(space, str) and 'N/A' in space:
        return space
    else:
        # Converte para string e remove tudo que não é número e espaço
        return re.sub(r'\s*m2$', '', str(space)).strip()

df['Living Space (m²)'] = df['Living Space (m²)'].apply(extract_numeric_space)

# Adicionar colunas para cidade e país
df['City'] = 'Genève'
df['Country'] = 'Switzerland'

# Definir a ordem das colunas
columns_order = ['Title', 'Rent (CHF)', 'Rooms', 'Living Space (m²)', 'Address', 'City', 'Country','Link']
df = df.reindex(columns=columns_order)

# Salvar a nova planilha
new_file_path = 'apartamentos_geneva_updated.xlsx'
df.to_excel(new_file_path, index=False)

print(f"Planilha atualizada e salva como '{new_file_path}'.")
