from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

chrome_options = Options()
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Navegar até a página desejada
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")  # Substitua pelo URL real

# Esperar até que o container com os resultados esteja presente
wait = WebDriverWait(driver, 10)
container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")))

# Encontre todos os apartamentos dentro do contêiner
apartamentos = container.find_elements(By.CLASS_NAME, "ResultList_listItem_j5Td_")

for apto in apartamentos:
    # Abra o link do apartamento na aba atual
    apto_link = apto.find_element(By.TAG_NAME, 'a').get_attribute('href')
    driver.get(apto_link)

    # Esperar até que a seção de detalhes esteja carregada
    detalhes = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hg-listing-details")))

    # Raspar os dados da seção desejada
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    detalhes = soup.find('section', {'class': 'hg-listing-details'})

    # Extraia as informações relevantes
    if detalhes:
        titulo = detalhes.find('h1', {'class': 'ListingTitle_spotlightTitle_ENVSi'}).text
        aluguel = detalhes.find('div', {'class': 'SpotlightAttributesPrice_value_TqKGz'}).text
        quartos = detalhes.find('div', {'class': 'SpotlightAttributesNumberOfRooms_value_TUMrd'}).text
        espaco = detalhes.find('div', {'class': 'SpotlightAttributesUsableSpace_value_cpfrh'}).text
        endereco = detalhes.find('address', {'class': 'AddressDetails_address_i3koO'}).text

        # Imprima ou salve os dados
        print(f"Título: {titulo}, Aluguel: {aluguel}, Quartos: {quartos}, Espaço: {espaco}, Endereço: {endereco}")

    # Voltar para a página de resultados
    driver.back()
    time.sleep(2)  # Pequena pausa para evitar problemas de carregamento

driver.quit()
