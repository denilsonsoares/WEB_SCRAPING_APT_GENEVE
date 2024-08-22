import pandas as pd
import ast
import folium
from folium.plugins import HeatMap
from branca.colormap import linear

def parse_price_date(price_date_str):
    """Função para extrair o preço a partir da string"""
    try:
        price_date = ast.literal_eval(price_date_str)
        return price_date[0][0]
    except:
        return None

def parse_coordinates(coord_str):
    """Função para extrair coordenadas da string"""
    try:
        coords = ast.literal_eval(coord_str)
        return coords
    except:
        return None

def plot_price_heatmap(input_file, output_html):
    # Lê a planilha do Excel com os dados
    df = pd.read_excel(input_file)

    if not {'Living Space (m²)', 'Price and Date', 'Coordinates'}.issubset(df.columns):
        raise ValueError("A planilha deve conter as colunas 'Living Space (m²)', 'Price and Date', e 'Coordinates'.")

    # Extraindo o preço e calculando o preço por metro quadrado
    df['Price'] = df['Price and Date'].apply(parse_price_date)
    df[['Latitude', 'Longitude']] = df['Coordinates'].apply(parse_coordinates).apply(pd.Series)
    df['Price per m²'] = df['Price'] / df['Living Space (m²)']
    df = df.dropna(subset=['Latitude', 'Longitude', 'Price per m²'])

    # Cria o mapa centrado na média das coordenadas
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)

    # Definir colormap com a escala correta: verde (barato) para vermelho (caro)
    colormap = linear.YlOrRd_09.scale(df['Price per m²'].min(), df['Price per m²'].max())
    colormap.caption = 'Price per m² (Cheap = Green, Expensive = Red)'

    # Gerar dados para o HeatMap
    heat_data = df[['Latitude', 'Longitude', 'Price per m²']].values.tolist()

    # Adicionar HeatMap ao mapa com o gradiente ajustado
    HeatMap(heat_data, min_opacity=0.5, radius=15, blur=15, gradient={0: 'green', 0.5: 'yellow', 1: 'red'}).add_to(m)

    # Adicionar a legenda ao mapa
    colormap.add_to(m)

    # Salvar o mapa como HTML
    m.save(output_html)
    print(f"Mapa de calor salvo com sucesso em: {output_html}")

# Exemplo de uso
input_file = "enderecos_com_coordenadas.xlsx"  # Substitua pelo caminho do seu arquivo com os dados
output_html = "price_heatmap.html"  # Nome do arquivo de saída (mapa de calor)

plot_price_heatmap(input_file, output_html)
