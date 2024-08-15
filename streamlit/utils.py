import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import pandas as pd
import time
import pytz
from datetime import datetime


# Função para criar o scraper com rotação de User-Agent
def criar_scraper():
    user_agent = UserAgent().random
    return cloudscraper.create_scraper(browser={'custom': user_agent})


# Função para criar o WebDriver com rotação de User-Agent e modo incógnito
def criar_driver():
    user_agent = UserAgent().random
    chrome_options = Options()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--incognito")
    return webdriver.Chrome(options=chrome_options)


# Função para lidar com o banner de privacidade
def lidar_com_privacidade(driver):
    try:
        wait = WebDriverWait(driver, 10)
        if WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler"))):
            reject_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
            reject_button.click()
            print("Banner de privacidade fechado.")
        else:
            print("Banner de privacidade não encontrado.")
    except Exception as e:
        print(f"Erro ao tentar fechar o banner de privacidade: {str(e)} - Prosseguindo...")


# Função genérica para coletar dados de apartamentos
def coletar_dados_apartamentos(driver, container_selector, titulo_selector, aluguel_selector,
                               quartos_selector, espaco_selector, endereco_selector, link_selector,
                               dados_apartamentos):
    tz = pytz.timezone('Europe/Zurich')
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, container_selector)))
    apartamentos = driver.find_elements(By.CSS_SELECTOR, container_selector)

    for apto in apartamentos:
        try:
            titulo = apto.find_element(By.CSS_SELECTOR, titulo_selector).text if titulo_selector else 'N/A'
            aluguel = apto.find_element(By.CSS_SELECTOR, aluguel_selector).text if aluguel_selector else 'N/A'
            quartos_element = apto.find_element(By.CSS_SELECTOR, quartos_selector)
            espaco_elementos = apto.find_elements(By.CSS_SELECTOR, espaco_selector)

            quartos = quartos_element.text if quartos_element else 'N/A'
            espaco = espaco_elementos[1].text if len(espaco_elementos) > 1 else 'N/A'

            endereco = apto.find_element(By.CSS_SELECTOR, endereco_selector).text if endereco_selector else 'N/A'
            link = apto.find_element(By.CSS_SELECTOR, link_selector).get_attribute('href') if link_selector else 'N/A'
            data_extracao = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            dados_apartamentos.append({
                'Título': titulo,
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })

            print(
                f"Título: {titulo}, Aluguel: {aluguel}, Quartos: {quartos}, Espaco: {espaco}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue

        time.sleep(1)


# Função genérica para navegar pelas páginas e coletar dados
def navegar_paginas(driver, scraper, url, container_selector, titulo_selector, aluguel_selector,
                    quartos_selector, espaco_selector, endereco_selector, link_selector):
    dados_apartamentos = []
    driver.get(url)
    lidar_com_privacidade(driver)

    while True:
        coletar_dados_apartamentos(driver, container_selector, titulo_selector, aluguel_selector,
                                   quartos_selector, espaco_selector, endereco_selector, link_selector,
                                   dados_apartamentos)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Go to next page']")
            if next_button and next_button.get_attribute('href'):
                next_button_href = next_button.get_attribute('href')
                print(f"Mudando para a próxima página: {next_button_href}")

                for attempt in range(5):
                    scraper = criar_scraper()
                    response = scraper.get(next_button_href)

                    if response.status_code == 200:
                        driver.quit()
                        driver = criar_driver()
                        driver.get(next_button_href)
                        lidar_com_privacidade(driver)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, container_selector)))
                        break
                    elif response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        print(f"Erro 429 recebido. Aguardando {retry_after} segundos antes de tentar novamente.")
                        time.sleep(retry_after)
                    else:
                        print(f"Falha ao acessar a próxima página: Status Code {response.status_code}")
                        break
            else:
                print("Botão 'Próxima página' está desabilitado ou não encontrado.")
                break
        except Exception as e:
            print(f"Não há mais páginas para processar ou ocorreu um erro: {str(e)}")
            break

    return pd.DataFrame(dados_apartamentos)


# Função principal de raspagem que integra tudo
def raspar_dados(site, tipo, cidade):
    if site == "homegate":
        if tipo == "alugar":
            url = f"https://www.homegate.ch/rent/apartment/{'city-' if cidade == 'Zurich' else 'canton-'}{cidade.lower()}/matching-list"
        else:
            url = f"https://www.homegate.ch/buy/apartment/{'city-' if cidade == 'Zurich' else 'canton-'}{cidade.lower()}/matching-list"
        container_selector = "div[role='listitem'][data-test='result-list-item']"
        titulo_selector = ".HgListingDescription_title_NAAxy span"
        aluguel_selector = ".HgListingCard_price_JoPAs"
        quartos_selector = ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:first-child > strong"
        espaco_selector = ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span"
        endereco_selector = ".HgListingCard_address_JGiFv"
        link_selector = "a.HgCardElevated_link_EHfr7"

    elif site == "immoscout24":
        if tipo == "alugar":
            url = f"https://www.immoscout24.ch/en/real-estate/rent/{'city-zuerich' if cidade == 'Zurich' else 'canton-geneve'}"
        else:
            url = f"https://www.immoscout24.ch/en/real-estate/buy/{'city-zuerich' if cidade == 'Zurich' else 'canton-geneve'}"
        container_selector = "div[role='listitem'][data-test='result-list-item']"
        titulo_selector = ".HgListingDescription_title_NAAxy span"
        aluguel_selector = ".HgListingRoomsLivingSpacePrice_price_u9Vee"
        quartos_selector = ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:first-child"
        espaco_selector = ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:nth-child(3)"
        endereco_selector = "div.HgListingCard_address_JGiFv address"
        link_selector = "a.HgCardElevated_link_EHfr7"

    driver = criar_driver()
    scraper = criar_scraper()

    try:
        df = navegar_paginas(driver, scraper, url, container_selector, titulo_selector, aluguel_selector,
                             quartos_selector, espaco_selector, endereco_selector, link_selector)
        df.to_excel(f"{tipo}_{site}_{cidade.lower()}.xlsx", index=False)
        print(f"Dados salvos em '{tipo}_{site}_{cidade.lower()}.xlsx'.")
    finally:
        driver.quit()

    return df
