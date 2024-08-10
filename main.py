from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome()  # Use o caminho correto para o seu driver
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")

# Encontre o contêiner que possui todos os apartamentos
container = driver.find_element(By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")

# Encontre todos os apartamentos dentro do contêiner
apartamentos = container.find_elements(By.CLASS_NAME, "ResultList_listItem_j5Td_")

for apto in apartamentos:
    # Abra o link do apartamento em uma nova aba
    apto_link = apto.find_element(By.TAG_NAME, 'a').get_attribute('href')
    driver.execute_script(f"window.open('{apto_link}', '_blank');")

    # Mude para a nova aba
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)  # Espere a página carregar

    # Raspe os dados da seção desejada
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

    # Feche a aba e volte para a aba original
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

driver.quit()

