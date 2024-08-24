import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time


def coletar_dados_apartamentos_bayut(soup, dados_apartamentos):
    tz = pytz.timezone('Asia/Dubai')
    apartamentos = soup.select("ul.e20beb46 > li.a37d52f0")  # Seletor ajustado

    for apto in apartamentos:
        try:
            # Extrair o JSON com as informações do imóvel
            json_script = apto.select_one("script[type='application/ld+json']")
            if json_script:
                json_data = json.loads(json_script.string)

                # Extrair título
                titulo = json_data.get('name', 'N/A')

                # Extrair o preço
                preco_element = apto.select_one("h4._0e3d05b8._5d2c9c26 > div._2923a568")
                if preco_element:
                    currency = preco_element.select_one("span._06f65f02").text.strip()
                    valor = preco_element.select_one("span.dc381b54").text.strip()
                    frequencia = apto.select_one("span.fc7b94b8").text.strip()
                    preco = f"{currency} {valor} ({frequencia})"
                else:
                    preco = 'N/A'

                # Tipo de transação
                tipo_transacao = "Aluguel"  # Valor fixo, como antes

                # Extrair a quantidade de quartos ou verificar se é um estúdio
                quartos = json_data.get('numberOfRooms', {}).get('value', 'N/A')
                if quartos == '0':
                    if 'Studio' in apto.text:
                        quartos = 'Studio'
                    else:
                        quartos = 'N/A'

                # Extrair o número de banheiros
                banheiros = json_data.get('numberOfBathroomsTotal', 'N/A')

                # Extrair o espaço (área)
                espaco = json_data.get('floorSize', {}).get('value', 'N/A') + " " + json_data.get('floorSize', {}).get('unitText', 'N/A')

                # Extrair o endereço
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
    # Configurar o WebDriver para rodar em modo headless e desabilitar imagens
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executar em modo invisível
    chrome_options.add_argument("--disable-gpu")  # Necessário para alguns sistemas operacionais
    chrome_options.add_argument("--window-size=1920x1080")  # Define o tamanho da janela (opcional)
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-extensions")  # Desabilitar extensões
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Desabilitar imagens, CSS, fontes e outros recursos para acelerar o carregamento
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.cookies": 2,
        "profile.managed_default_content_settings.javascript": 1,  # Habilitar JavaScript (necessário para Selenium)
        "profile.managed_default_content_settings.plugins": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.geolocation": 2,
        "profile.managed_default_content_settings.notifications": 2,
        "profile.managed_default_content_settings.auto_select_certificate": 2,
        "profile.managed_default_content_settings.media_stream": 2,
        "profile.managed_default_content_settings.site_engagement": 2,
        "profile.managed_default_content_settings.sound": 2,
        "profile.managed_default_content_settings.automatic_downloads": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Inicializa o WebDriver com as opções configuradas
    driver = webdriver.Chrome(options=chrome_options)

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
