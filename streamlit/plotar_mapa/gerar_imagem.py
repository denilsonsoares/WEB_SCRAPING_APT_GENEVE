from selenium import webdriver
import time


def save_map_as_png(map_html, output_png):
    # Configure o WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1200x800')

    driver = webdriver.Chrome(options=options)

    # Carregue o mapa
    driver.get(f'file://{map_html}')

    # Aguarde o mapa carregar
    time.sleep(5)

    # Capture a tela e salve como PNG
    driver.save_screenshot(output_png)
    driver.quit()


# Exemplo de uso
map_html = "price_heatmap.html"  # HTML gerado pelo Folium
output_png = "price_heatmap.png"  # Nome do arquivo PNG

save_map_as_png(map_html, output_png)
print(f"Imagem salva com sucesso em: {output_png}")
