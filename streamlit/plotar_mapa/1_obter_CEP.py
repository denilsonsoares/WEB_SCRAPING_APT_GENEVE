import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta


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


def extract_valid_price_and_date(price_date_list):
    # Converte a string em uma lista de tuplas (preço, data)
    price_date_tuples = eval(price_date_list)

    # Define o dia atual e o dia anterior
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Filtra as tuplas que têm a data correspondente ao dia de hoje ou ao dia anterior
    valid_tuples = [pd for pd in price_date_tuples if datetime.strptime(pd[1], '%Y-%d-%m').date() in {today, yesterday}]

    if not valid_tuples:
        return None, None

    # Seleciona a tupla com a data mais recente
    latest_tuple = max(valid_tuples, key=lambda pd: datetime.strptime(pd[1], '%Y-%d-%m').date())

    return latest_tuple


def generate_cep_excel(input_file, output_file, num_apartments, transaction_type):
    # Lê a planilha do Excel
    df = pd.read_excel(input_file)

    # Checa se as colunas necessárias estão presentes
    if not {'Address', 'City', 'Country', 'Price and Date', 'Type of Transaction'}.issubset(df.columns):
        raise ValueError(
            "A planilha deve conter as colunas 'Address', 'City', 'Country', 'Price and Date' e 'Type of Transaction'.")

    # Filtra os dados pelo tipo de transação (Rent ou Buy)
    df = df[df['Type of Transaction'] == transaction_type]

    # Extrai o preço e a data válidos (dia atual ou dia anterior)
    df[['Latest Price', 'Latest Date']] = df['Price and Date'].apply(
        lambda x: pd.Series(extract_valid_price_and_date(x)))

    # Remove as linhas onde não há preços válidos
    df = df.dropna(subset=['Latest Price', 'Latest Date'])

    # Ordena pelo preço mais barato
    df = df.sort_values(by='Latest Price').head(num_apartments)

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
num_apartments = 100  # Defina quantos apartamentos deseja processar
transaction_type = "Rent"  # Escolha entre "Rent" ou "Buy"

generate_cep_excel(input_file, output_file, num_apartments, transaction_type)
print(f"Arquivo salvo com sucesso em: {output_file}")
