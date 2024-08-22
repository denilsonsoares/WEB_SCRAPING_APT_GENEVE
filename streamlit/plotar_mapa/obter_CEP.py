import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def get_cep_from_address(address, city, country="Switzerland"):
    try:
        # Inicializa o geocodificador Nominatim
        geolocator = Nominatim(user_agent="address-to-cep")
        full_address = f"{address}, {city}, {country}"

        # Realiza a geocodificação
        location = geolocator.geocode(full_address)

        if location:
            # Retorna o CEP (pode precisar ajustar o parsing dependendo do formato suíço)
            return location.raw.get('display_name').split(',')[-2].strip()
        else:
            return None
    except:
        return None

def generate_cep_excel(input_file, output_file):
    # Lê a planilha do Excel
    df = pd.read_excel(input_file)

    # Checa se as colunas necessárias estão presentes
    if not {'Address', 'City', 'Country'}.issubset(df.columns):
        raise ValueError("A planilha deve conter as colunas 'Address', 'City' e 'Country'.")

    # Aplica a função para gerar o CEP e cria uma nova coluna 'CEP'
    df['CEP'] = df.apply(lambda row: get_cep_from_address(row['Address'], row['City'], row['Country']), axis=1)

    # Reorganiza as colunas para que 'CEP' esteja após 'Country'
    columns_order = df.columns.tolist()
    columns_order.insert(columns_order.index('Country') + 1, columns_order.pop(columns_order.index('CEP')))
    df = df[columns_order]

    # Salva a nova planilha com os CEPs
    df.to_excel(output_file, index=False)

# Exemplo de uso
input_file = "enderecos.xlsx"  # Substitua pelo caminho do seu arquivo
output_file = "enderecos_com_cep.xlsx"  # Nome do arquivo de saída

generate_cep_excel(input_file, output_file)
print(f"Arquivo salvo com sucesso em: {output_file}")
