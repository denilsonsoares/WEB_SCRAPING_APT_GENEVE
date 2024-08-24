import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time


def coletar_dados_apartamentos_bayut(soup, dados_apartamentos):
    tz = pytz.timezone('Asia/Dubai')
    apartamentos = soup.select("ul.e20beb46 > li.a37d52f0")  # Ajuste no seletor para corresponder aos elementos 'li'

    for apto in apartamentos:
        try:
            # Tenta extrair o título
            titulo_element = apto.select_one("article .d40f2294[title]")
            titulo = titulo_element['title'] if titulo_element else 'N/A'

            # Tenta extrair o preço (ajustando conforme a estrutura do site)
            preco_element = apto.find("script", type="application/ld+json")
            preco = 'N/A'
            if preco_element:
                json_data = json.loads(preco_element.string)
                preco = json_data.get('floorSize', {}).get('value', 'N/A') + " " + json_data.get('floorSize', {}).get('unitText', 'N/A')

            # Tipo de transação
            tipo_transacao = "Aluguel"  # Valor fixo, como antes

            # Tenta extrair a quantidade de quartos
            quartos = json_data.get('numberOfRooms', {}).get('value', 'N/A')
            if quartos == 'N/A':  # Verifica se o valor não foi encontrado e tenta achar um Studio
                studio_element = apto.select_one("span[aria-label='Studio']")
                if studio_element:
                    quartos = "Studio"

            # Tenta extrair o número de banheiros
            banheiros = json_data.get('numberOfBathroomsTotal', 'N/A')

            # Tenta extrair o espaço (área)
            espaco = json_data.get('floorSize', {}).get('value', 'N/A') + " " + json_data.get('floorSize', {}).get('unitText', 'N/A')

            # Tenta extrair o endereço
            endereco = json_data.get('address', {}).get('addressLocality', 'N/A') + ", " + json_data.get('address', {}).get('addressRegion', 'N/A')

            # Link para o site do imóvel
            link = json_data.get('url', 'N/A')

            # Data de extração
            data_extracao = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            dados_apartamentos.append({
                'Título': titulo,
                'Preço': preco,
                'Tipo de Transação': tipo_transacao,
                'Quartos': quartos,
                'Espaço': espaco,
                'Banheiros': banheiros,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })
            print(f"Título: {titulo}, Preço: {preco}, Tipo de Transação: {tipo_transacao}, Quartos: {quartos}, Espaço: {espaco}, Banheiros: {banheiros}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue


def raspar_apartamentos_com_selenium(url_inicial):
    # Configurar o WebDriver (no caso, utilizando o Chrome)
    driver = webdriver.Chrome()  # Verifique se o chromedriver está no PATH ou forneça o caminho completo
    driver.get(url_inicial)

    dados_apartamentos = []

    while True:
        try:
            # Aguarda o carregamento da página
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.e20beb46")))

            # Obter o conteúdo da página atual
            soup = BeautifulSoup(driver.page_source, 'lxml')
            coletar_dados_apartamentos_bayut(soup, dados_apartamentos)

            try:
                # Tenta encontrar o botão de próxima página
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[title='Next']"))
                )
                next_button.click()
                time.sleep(3)  # Aguardar o carregamento da próxima página
            except Exception:
                print("Não há mais páginas a serem raspadas.")
                break

        except Exception as e:
            print(f"Erro durante a navegação ou raspagem: {str(e)}")
            break

    driver.quit()

    # Convertendo para DataFrame ao final da coleta
    df_apartamentos = pd.DataFrame(dados_apartamentos)
    return df_apartamentos


# URL inicial da página
url_inicial = "https://www.bayut.com/to-rent/apartments/dubai/business-bay/aykon-city/"

# Executa a raspagem e armazena os dados em um DataFrame
df_apartamentos = raspar_apartamentos_com_selenium(url_inicial)

# Imprime o DataFrame final
print(df_apartamentos)

# Salva o DataFrame em um arquivo Excel
df_apartamentos.to_excel("dados_dubai.xlsx", index=False)

print("Dados salvos em 'dados_dubai.xlsx'")

