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
    apartamentos = soup.select("ul.e20beb46 > div._475e888a._5d46b9fb")

    for apto in apartamentos:
        try:
            # Tenta extrair o título
            titulo_element = apto.select_one("h2.f0f13906")
            titulo = titulo_element.get_text(strip=True) if titulo_element else 'N/A'

            # Tenta extrair o preço
            preco_element = apto.select_one("span[aria-label='Price']")
            preco = preco_element.get_text(strip=True) if preco_element else 'N/A'

            # Tenta extrair o tipo de transação
            tipo_transacao = "Aluguel"  # Como a página é de aluguel, este valor será fixo

            # Tenta extrair a quantidade de quartos
            quartos_element = apto.select_one("span[aria-label='Beds']")
            quartos = quartos_element.get_text(strip=True) if quartos_element else 'N/A'

            # Tenta extrair o número de banheiros
            banheiros_element = apto.select_one("span[aria-label='Baths']")
            banheiros = banheiros_element.get_text(strip=True) if banheiros_element else 'N/A'

            # Tenta extrair o espaço (área)
            espaco_element = apto.select_one("span[aria-label='Area'] h4")
            espaco = espaco_element.get_text(strip=True) if espaco_element else 'N/A'

            # Tenta extrair o endereço
            endereco_element = apto.select_one("h3._4402bd70")
            endereco = endereco_element.get_text(strip=True) if endereco_element else 'N/A'

            # Link para o site do imóvel
            link_element = apto.select_one("a")
            link = "https://www.bayut.com" + link_element['href'] if link_element else 'N/A'

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
    return dados_apartamentos

# URL inicial da página
url_inicial = "https://www.bayut.com/to-rent/apartments/dubai/business-bay/aykon-city/"

# Executa a raspagem
dados_apartamentos = raspar_apartamentos_com_selenium(url_inicial)

# Aqui você pode salvar os dados ou fazer outras operações
print(dados_apartamentos)
