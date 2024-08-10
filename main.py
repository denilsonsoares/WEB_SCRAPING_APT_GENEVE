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

# Função para coletar dados da página
def coletar_dados_apartamentos():
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


# Loop para navegar pelas páginas
while True:
    coletar_dados_apartamentos()

    try:
        # Tente encontrar o botão "Próxima página"
        next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Go to next page']")

        # Verifique se o botão não está desabilitado
        if next_button:
            next_button_href = next_button.get_attribute('href')
            print(f"Mudando para a próxima página: {next_button_href}")

            # Tentar acessar a próxima página, com tratamento para erro 429
            for attempt in range(5):  # Tentar até 5 vezes
                response = scraper.get(next_button_href, cookies=cookies, headers={'User-Agent': user_agent})

                if response.status_code == 200:
                    # Parsear a nova página com BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Atualizar o container com a nova página
                    container_html = soup.find('div', {'class': 'ResultListPage_resultListPage_iq_V2'})
                    if container_html:
                        driver.execute_script("arguments[0].innerHTML = arguments[1];", container, container_html.prettify())
                    else:
                        print("Não foi possível atualizar o container para a nova página.")
                        break
                    break  # Sair do loop de tentativa
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 120))  # Tempo de espera sugerido ou padrão de 60 segundos
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

# Criar um DataFrame do pandas com os dados coletados
df = pd.DataFrame(dados_apartamentos)

# Salvar o DataFrame em um arquivo Excel
df.to_excel("apartamentos_geneva.xlsx", index=False)

print("Dados salvos em 'apartamentos_geneva.xlsx'.")
