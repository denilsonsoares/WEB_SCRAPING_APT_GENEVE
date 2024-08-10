from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Inicializando o WebDriver (use o caminho correto para o WebDriver)
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')

# Acesse a página principal
driver.get('https://www.homegate.ch/rent/apartment/canton-geneva/matching-list')

# Encontrar todos os apartamentos listados
apartments = driver.find_elements(By.CSS_SELECTOR, 'div[data-test="result-list-item"]')

# Iterar sobre os apartamentos
for apt in apartments:
    # Abrir o apartamento em uma nova aba
    apt_link = apt.find_element(By.TAG_NAME, 'a')
    apt_link.send_keys(Keys.CONTROL + Keys.RETURN)
    driver.switch_to.window(driver.window_handles[-1])

    # Esperar a página carregar
    time.sleep(3)

    # Raspar as informações relevantes da página de detalhes
    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1.ListingTitle_spotlightTitle_ENVSi').text
        rent = driver.find_element(By.CSS_SELECTOR, 'div.SpotlightAttributesPrice_value_TqKGz span').text
        rooms = driver.find_element(By.CSS_SELECTOR, 'div.SpotlightAttributesNumberOfRooms_value_TUMrd').text
        living_space = driver.find_element(By.CSS_SELECTOR, 'div.SpotlightAttributesUsableSpace_value_cpfrh').text
        address = driver.find_element(By.CSS_SELECTOR, 'address.AddressDetails_address_i3koO').text

        # Exibir os dados coletados (ou salvar em um arquivo)
        print(f"Title: {title}, Rent: {rent}, Rooms: {rooms}, Living Space: {living_space}, Address: {address}")
    except Exception as e:
        print("Error scraping apartment details:", e)

    # Fechar a aba atual e voltar para a lista de apartamentos
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Fechar o WebDriver
driver.quit()
