import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Inicializando o cloudscraper
scraper = cloudscraper.create_scraper()

# Configurando o WebDriver
chrome_options = Options()
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
chrome_options.add_argument("--incognito")  # Adicionando modo incógnito
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Função para lidar com o banner de privacidade
def lidar_com_privacidade():
    try:
        # Espera o botão "Alle ablehnen" estar presente e clica nele
        wait = WebDriverWait(driver, 10)
        reject_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
        reject_button.click()
        print("Banner de privacidade fechado.")
    except Exception as e:
        print(f"Erro ao lidar com o banner de privacidade: {str(e)}")

# Carregar a página inicial
driver.get("https://www.homegate.ch/rent/apartment/canton-geneva/matching-list")

# Lidar com o banner de privacidade
lidar_com_privacidade()

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

# Função para coletar dados da lista de apartamentos diretamente
def coletar_dados_apartamentos():
    # Encontre todos os apartamentos dentro do contêiner
    apartamentos = container.find_elements(By.CSS_SELECTOR, "div[role='listitem'][data-test='result-list-item']")

    for apto in apartamentos:
        try:
            # Obter o link do apartamento
            apto_link = apto.find_element(By.TAG_NAME, 'a').get_attribute('href')

            # Verificar e obter o aluguel
            aluguel_element = apto.find_element(By.CLASS_NAME, 'HgListingCard_price_JoPAs')
            aluguel = aluguel_element.text if aluguel_element else 'N/A'

            # Verificar e obter o número de quartos
            quartos_element = apto.find_element(By.XPATH, ".//span[contains(@class, 'HgListingCard_infoItem_Lfs2R')]")
            quartos = quartos_element.text if quartos_element else 'N/A'

            # Verificar e obter o espaço
            espaco_element = apto.find_element(By.XPATH, ".//span[contains(text(),'m²')]")
            espaco = espaco_element.text if espaco_element else 'N/A'

            # Verificar e obter o endereço
            endereco_element = apto.find_element(By.CLASS_NAME, 'HgListingCard_address_Zb0Cr')
            endereco = endereco_element.text if endereco_element else 'N/A'

            # Adicionar os dados do apartamento na lista
            dados_apartamentos.append({
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': apto_link
            })

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue  # Continuar com o próximo item, mesmo em caso de erro

        time.sleep(1)  # Pequena pausa para evitar problemas de carregamento


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
                    # Atualizar o container da nova página
                    driver.get(next_button_href)
                    #lidar_com_privacidade()  # Lidar com o banner de privacidade na nova página
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ResultListPage_resultListPage_iq_V2")))
                    break  # Sair do loop de tentativa
                elif response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))  # Tempo de espera sugerido ou padrão de 60 segundos
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
df.to_excel("homegate_geneva.xlsx", index=False)

print("Dados salvos em 'homegate_geneva.xlsx'.")
