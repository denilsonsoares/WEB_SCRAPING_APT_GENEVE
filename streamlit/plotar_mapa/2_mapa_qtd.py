import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
from branca.colormap import linear
from ast import literal_eval

def get_coordinates_from_cep(cep, country="Switzerland"):
    try:
        geolocator = Nominatim(user_agent="cep-to-coordinates")
        location = geolocator.geocode(cep, country_codes='CH')
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except:
        return None

def extract_latest_price(price_date_str):
    price_date_list = literal_eval(price_date_str)
    latest_price = max(price_date_list, key=lambda x: x[1])
    return latest_price[0]

def plot_heatmap_and_save_excel(input_file, output_html, output_excel, order_by="Price", city_filter=None):
    df = pd.read_excel(input_file)

    if 'CEP' not in df.columns:
        raise ValueError("A planilha deve conter a coluna 'CEP'.")

    # Filtrar por cidade, se city_filter for fornecido
    if city_filter:
        df = df[df['City'] == city_filter]

    df['CEP_Frequency'] = df.groupby('CEP')['CEP'].transform('count')
    df['Coordinates'] = df['CEP'].apply(get_coordinates_from_cep)
    df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Extrair o último preço de cada apartamento
    df['Latest_Price'] = df['Price and Date'].apply(extract_latest_price)

    # Calcular o preço por m²
    df['Price per m²'] = df['Latest_Price'] / df['Living Space (m²)']

    # Ordenar a tabela conforme a escolha
    if order_by == "Price per m²":
        df = df.sort_values(by='Price per m²', ascending=True)
    else:
        df = df.sort_values(by='Latest_Price', ascending=True)

    # Cria um mapa centrado na média das coordenadas
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)

    # Adiciona o HeatMap ao mapa
    heat_data = df[['Latitude', 'Longitude', 'CEP_Frequency']].values.tolist()
    HeatMap(heat_data).add_to(m)

    # Adiciona a legenda do mapa
    colormap = linear.YlOrRd_09.scale(df['CEP_Frequency'].min(), df['CEP_Frequency'].max())
    colormap.caption = 'Número de Apartamentos por CEP (Verde = Baixo, Vermelho = Alto)'
    colormap.add_to(m)

    # Cria uma tabela com os links, preços, preços por m² e o número de quartos
    table_html = f"""
    <div style='position: fixed; top: 100px; left: 80px; width: 600px; max-height: 300px; z-index:9999; background-color: white; padding: 10px; border: 2px solid grey; overflow-y: auto;'>
        <b>Visit the websites</b><br>
        <table border='1' style='width: 100%; border-collapse: collapse;'>
            <tr>
                <th>Link</th>
                <th>Price (CHF)</th>
                <th>Price per m²</th>
                <th>Rooms</th>
            </tr>
    """

    for _, row in df.iterrows():
        table_html += f"""
            <tr>
                <td><a href='{row['Extracted from']}' target='_blank'>{row['Extracted from']}</a></td>
                <td>{row['Latest_Price']}</td>
                <td>{row['Price per m²']:.2f}</td>
                <td>{row['Rooms']}</td>
            </tr>
        """

    table_html += "</table></div>"

    # Adiciona a tabela ao mapa
    m.get_root().html.add_child(folium.Element(table_html))

    # Salva o mapa como um arquivo HTML
    m.save(output_html)
    print(f"Mapa de calor salvo com sucesso em: {output_html}")

    # Salva a planilha com as novas colunas
    df.to_excel(output_excel, index=False)
    print(f"Nova planilha com coordenadas e frequências salva em: {output_excel}")

# Exemplo de uso
input_file = "enderecos_com_cep.xlsx"
output_html = "heatmap.html"
output_excel = "enderecos_com_coordenadas.xlsx"

# Ordenar por "Price" ou "Price per m²" e filtrar por cidade
plot_heatmap_and_save_excel(input_file, output_html, output_excel, order_by="Price per m²", city_filter="Zurich")
