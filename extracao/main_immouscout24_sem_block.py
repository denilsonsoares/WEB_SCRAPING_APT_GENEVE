import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import pandas as pd
import time


# Inicializando o cloudscraper com rotação de User-Agent
def criar_scraper():
    user_agent = UserAgent().random
    return cloudscraper.create_scraper(browser={'custom': user_agent})


scraper = criar_scraper()


# Configurando o WebDriver com rotação de User-Agent
def criar_driver():
    user_agent = UserAgent().random
    chrome_options = Options()
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--incognito")
    return webdriver.Chrome(options=chrome_options)


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


# Função para coletar dados da lista de apartamentos diretamente
def coletar_dados_apartamentos(driver, container, dados_apartamentos):
    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listitem'][data-test='result-list-item']")))
    apartamentos = container.find_elements(By.CSS_SELECTOR, "div[role='listitem'][data-test='result-list-item']")
    for apto in apartamentos:
        try:
            # Título
            titulo_element = apto.find_element(By.CSS_SELECTOR, "p.HgListingDescription_title_NAAxy span")
            titulo = titulo_element.text if titulo_element else 'N/A'

            # Aluguel
            aluguel_element = apto.find_element(By.CSS_SELECTOR, "span.HgListingRoomsLivingSpacePrice_price_u9Vee")
            aluguel = aluguel_element.text if aluguel_element else 'N/A'

            # Quartos e Espaço
            detalhes_element = apto.find_element(By.CSS_SELECTOR,
                                                 "div.HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp")
            detalhes = detalhes_element.text if detalhes_element else 'N/A'

            # Extraindo quartos e espaço
            quartos = detalhes.split(",")[0].strip() if detalhes else 'N/A'
            espaco = detalhes.split(",")[1].strip() if len(detalhes.split(",")) > 1 else 'N/A'

            # Endereço
            endereco_element = apto.find_element(By.CSS_SELECTOR, "div.HgListingCard_secondaryTitle_uVla3 address")
            endereco = endereco_element.text if endereco_element else 'N/A'

            dados_apartamentos.append({
                'Título': titulo,
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco
            })
            # Printando os dados coletados para acompanhar
            print(f"Título: {titulo}")
            print(f"Aluguel: {aluguel}")
            print(f"Quartos: {quartos}")
            print(f"Espaço: {espaco}")
            print(f"Endereço: {endereco}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue

        time.sleep(1)


# Loop para navegar pelas páginas
def navegar_paginas(driver, scraper, dados_apartamentos):
    while True:
        container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='result-list-container']"))
        )
        coletar_dados_apartamentos(driver, container, dados_apartamentos)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Go to next page']")
            if next_button and next_button.get_attribute('href'):
                next_button_href = next_button.get_attribute('href')
                print(f"Mudando para a próxima página: {next_button_href}")

                for attempt in range(5):  # Tentar até 5 vezes
                    scraper = criar_scraper()  # Atualizar o scraper com novo User-Agent
                    response = scraper.get(next_button_href)

                    if response.status_code == 200:
                        driver.quit()  # Fechar o driver antigo
                        driver = criar_driver()  # Criar um novo driver
                        driver.get(next_button_href)
                        lidar_com_privacidade(driver)
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='result-list-container']"))
                        )
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


# Execução principal
driver = criar_driver()
driver.maximize_window()

try:
    driver.get("https://www.immoscout24.ch/en/real-estate/rent/canton-geneva")
    lidar_com_privacidade(driver)
    dados_apartamentos = []
    navegar_paginas(driver, scraper, dados_apartamentos)
finally:
    driver.quit()

df = pd.DataFrame(dados_apartamentos)
df.to_excel("immoscout_geneva_total.xlsx", index=False)
print("Dados salvos em 'immoscout_geneva_total.xlsx'.")
