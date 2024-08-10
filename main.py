import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Inicializando o cloudscraper
scraper = cloudscraper.create_scraper()

# Configurando o WebDriver
chrome_options = Options()
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Carregar a página inicial
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")

# Obter cookies e headers para o Cloudflare
cookies, user_agent = scraper.get_tokens("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")

# Adicionar cookies ao driver
for name, value in cookies.items():
    driver.add_cookie({'name': name, 'value': value, 'domain': '.homegate.ch'})

# Recarregar a página para aplicar os cookies
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")

# Esperar até que o container com os resultados esteja presente
wait = WebDriverWait(driver, 20)
container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")))

# Lista para armazenar os dados dos apartamentos
dados_apartamentos = []

# Encontre todos os apartamentos dentro do contêiner
apartamentos = container.find_elements(By.CLASS_NAME, "ResultList_listItem_j5Td_")

for apto in apartamentos:
    # Obter o link do apartamento
    apto_link = apto.find_element(By.TAG_NAME, 'a').get_attribute('href')

    # Use cloudscraper para obter a página do apartamento
    response = scraper.get(apto_link)

    if response.status_code == 200:
        # Parsear a página com BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        detalhes = soup.find('section', {'class': 'hg-listing-details'})

        if detalhes:
            # Verificar e obter o título
            titulo_element = detalhes.find('h1', {'class': 'ListingTitle_spotlightTitle_ENVSi'})
            titulo = titulo_element.text if titulo_element else 'N/A'

            # Verificar e obter o aluguel
            aluguel_element = detalhes.find('div', {'class': 'SpotlightAttributesPrice_value_TqKGz'})
            aluguel = aluguel_element.text if aluguel_element else 'N/A'

            # Verificar e obter o número de quartos
            quartos_element = detalhes.find('div', {'class': 'SpotlightAttributesNumberOfRooms_value_TUMrd'})
            quartos = quartos_element.text if quartos_element else 'N/A'

            # Verificar e obter o espaço
            espaco_element = detalhes.find('div', {'class': 'SpotlightAttributesUsableSpace_value_cpfrh'})
            espaco = espaco_element.text if espaco_element else 'N/A'

            # Verificar e obter o endereço
            endereco_element = detalhes.find('address', {'class': 'AddressDetails_address_i3koO'})
            endereco = endereco_element.text if endereco_element else 'N/A'

            # Adicionar os dados do apartamento na lista
            dados_apartamentos.append({
                'Título': titulo,
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': apto_link
            })
    else:
        print(f"Falha ao acessar {apto_link}: Status Code {response.status_code}")

    time.sleep(2)  # Pequena pausa para evitar problemas de carregamento

driver.quit()

# Criar um DataFrame do pandas com os dados coletados
df = pd.DataFrame(dados_apartamentos)

# Salvar o DataFrame em um arquivo Excel
df.to_excel("apartamentos_geneva.xlsx", index=False)

print("Dados salvos em 'apartamentos_geneva.xlsx'.")
