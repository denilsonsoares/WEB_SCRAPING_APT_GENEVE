import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.map import Marker
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

def plot_apartments_map(input_file, output_html, order_by="Price", city_filter=None):
    df = pd.read_excel(input_file)

    if 'CEP' not in df.columns:
        raise ValueError("A planilha deve conter a coluna 'CEP'.")

    if city_filter:
        df = df[df['City'] == city_filter]

    df['CEP_Frequency'] = df.groupby('CEP')['CEP'].transform('count')
    df['Coordinates'] = df['CEP'].apply(get_coordinates_from_cep)
    df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)
    df = df.dropna(subset=['Latitude', 'Longitude'])

    df['Latest_Price'] = df['Price and Date'].apply(extract_latest_price)
    df['Price per m²'] = df['Latest_Price'] / df['Living Space (m²)']

    if order_by == "Price per m²":
        df = df.sort_values(by='Price per m²', ascending=True)
    else:
        df = df.sort_values(by='Latest_Price', ascending=True)

    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)

    # Agrupar apartamentos por coordenadas
    grouped = df.groupby(['Latitude', 'Longitude'])

    for (lat, lon), group in grouped:
        if len(group) == 1:
            # Apenas um apartamento
            row = group.iloc[0]
            popup_content = f"""
                <b>Link:</b> <a href='{row['Extracted from']}' target='_blank'>{row['Extracted from']}</a><br>
                <b>Price:</b> {row['Latest_Price']} CHF<br>
                <b>Price per m²:</b> {row['Price per m²']:.2f} CHF<br>
                <b>Rooms:</b> {row['Rooms']}
            """
        else:
            # Vários apartamentos na mesma localização
            popup_content = "<b>Multiple Apartments:</b><br>"
            for _, subrow in group.iterrows():
                popup_content += f"""
                    <b>Link:</b> <a href='{subrow['Extracted from']}' target='_blank'>{subrow['Extracted from']}</a><br>
                    <b>Price:</b> {subrow['Latest_Price']} CHF<br>
                    <b>Price per m²:</b> {subrow['Price per m²']:.2f} CHF<br>
                    <b>Rooms:</b> {subrow['Rooms']}<br><br>
                """

        Marker([lat, lon], popup=folium.Popup(popup_content, max_width=450)).add_to(m)

    m.save(output_html)
    print(f"Mapa de apartamentos salvo com sucesso em: {output_html}")

# Exemplo de uso
input_file = "enderecos_com_cep.xlsx"
output_html = "apartments_map.html"

# Ordenar por "Price" ou "Price per m²" e filtrar por cidade
plot_apartments_map(input_file, output_html, order_by="Price per m²", city_filter="Zurich")
