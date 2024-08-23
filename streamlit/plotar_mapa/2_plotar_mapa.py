import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
from branca.colormap import linear

def get_coordinates_from_cep(cep, country="Switzerland"):
    try:
        # Inicializa o geocodificador Nominatim
        geolocator = Nominatim(user_agent="cep-to-coordinates")

        # Obtém as coordenadas a partir do CEP
        location = geolocator.geocode(cep, country_codes='CH')

        if location:
            # Retorna as coordenadas (latitude, longitude)
            return (location.latitude, location.longitude)
        else:
            return None

    except:
        return None

def plot_heatmap_and_save_excel(input_file, output_html, output_excel):
    # Lê a planilha do Excel com os CEPs
    df = pd.read_excel(input_file)

    # Checa se a coluna 'CEP' está presente
    if 'CEP' not in df.columns:
        raise ValueError("A planilha deve conter a coluna 'CEP'.")

    # Conta a frequência de cada CEP
    df['CEP_Frequency'] = df.groupby('CEP')['CEP'].transform('count')

    # Aplica a função para converter CEP em coordenadas e cria duas novas colunas: 'Latitude' e 'Longitude'
    df['Coordinates'] = df['CEP'].apply(get_coordinates_from_cep)
    df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)

    # Filtra as linhas que têm coordenadas válidas
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Cria um mapa centrado na média das coordenadas
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)

    # Adiciona o HeatMap ao mapa, ponderado pela frequência dos CEPs
    heat_data = df[['Latitude', 'Longitude', 'CEP_Frequency']].values.tolist()
    HeatMap(heat_data).add_to(m)

    # Adiciona uma legenda ao mapa
    colormap = linear.YlOrRd_09.scale(df['CEP_Frequency'].min(), df['CEP_Frequency'].max())
    colormap.caption = 'Número de Apartamentos por CEP (Verde = Baixo, Vermelho = Alto)'
    colormap.add_to(m)

    # Salva o mapa como um arquivo HTML
    m.save(output_html)
    print(f"Mapa de calor salvo com sucesso em: {output_html}")

    # Salva a planilha com as novas colunas de latitude, longitude e frequência
    df.to_excel(output_excel, index=False)
    print(f"Nova planilha com coordenadas e frequências salva em: {output_excel}")

# Exemplo de uso
input_file = "enderecos_com_cep.xlsx"  # Substitua pelo caminho do seu arquivo com CEPs
output_html = "heatmap.html"  # Nome do arquivo de saída (mapa de calor)
output_excel = "enderecos_com_coordenadas.xlsx"  # Nome do arquivo de saída com coordenadas

plot_heatmap_and_save_excel(input_file, output_html, output_excel)
