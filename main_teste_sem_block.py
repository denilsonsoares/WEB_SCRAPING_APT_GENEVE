import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import pandas as pd
import time
import random

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

driver = criar_driver()
driver.maximize_window()

# Função para lidar com o banner de privacidade
def lidar_com_privacidade():
    try:
        wait = WebDriverWait(driver, 2)
        reject_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
        reject_button.click()
        print("Banner de privacidade fechado.")
    except Exception as e:
        print(f"Banner de privacidade não encontrado ou erro ao tentar fechar: {str(e)} - Prosseguindo...")

# Carregar a página inicial
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")
lidar_com_privacidade()

# Esperar até que o container com os resultados esteja presente
wait = WebDriverWait(driver, 20)
container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")))

# Lista para armazenar os dados dos apartamentos
dados_apartamentos = []

# Função para coletar dados da lista de apartamentos diretamente
def coletar_dados_apartamentos():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listitem'][data-test='result-list-item']")))
    apartamentos = container.find_elements(By.CSS_SELECTOR, "div[role='listitem'][data-test='result-list-item']")
    for apto in apartamentos:
        try:
            aluguel_element = apto.find_element(By.CLASS_NAME, 'HgListingCard_price_JoPAs')
            aluguel = aluguel_element.text if aluguel_element else 'N/A'

            quartos_element = apto.find_element(By.CSS_SELECTOR, ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:first-child > strong")
            quartos = quartos_element.text + " room(s)" if quartos_element else 'N/A'

            espaco_element = apto.find_element(By.CSS_SELECTOR, ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:last-child > strong")
            espaco = espaco_element.text + " m²" if espaco_element else 'N/A'

            endereco_element = apto.find_element(By.CLASS_NAME, 'HgListingCard_address_JGiFv')
            endereco = endereco_element.text if endereco_element else 'N/A'

            dados_apartamentos.append({
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco
            })

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue

        time.sleep(1)

# Loop para navegar pelas páginas
while True:
    coletar_dados_apartamentos()

    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Go to next page']")
        if next_button and next_button.get_attribute('href'):
            next_button_href = next_button.get_attribute('href')
            print(f"Mudando para a próxima página: {next_button_href}")

            for attempt in range(5):  # Tentar até 5 vezes
                scraper = criar_scraper()  # Atualizar o scraper com novo User-Agent
                response = scraper.get(next_button_href)

                if response.status_code == 200:
                    driver.get(next_button_href)
                    lidar_com_privacidade()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")))
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

driver.quit()

df = pd.DataFrame(dados_apartamentos)
df.to_excel("homegate_geneva.xlsx", index=False)
print("Dados salvos em 'homegate_geneva.xlsx'.")
