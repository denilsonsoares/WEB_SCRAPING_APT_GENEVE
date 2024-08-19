import time
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def rolar_pagina_gradualmente(driver, duracao=20, intervalo=0.2):
    # Rola a página gradualmente por 'duracao' segundos com 'intervalo' segundos entre cada rolagem
    tempo_final = time.time() + duracao
    while time.time() < tempo_final:
        driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.1);")
        time.sleep(intervalo)

def coletar_dados_apartamentos_zapimoveis(driver, dados_apartamentos):
    # Rolar a página para carregar todo o conteúdo
    rolar_pagina_gradualmente(driver)

    # Verifica se o botão de 'Próxima página' está presente e clique nele
    try:
        next_button = driver.find_element(By.XPATH, "//button[@data-testid='next-page']")
        if next_button.is_displayed():
            next_button.click()
            time.sleep(2)  # Aguarda a página carregar
            return True  # Indica que há uma próxima página para processar
    except:
        pass

    # Extrair conteúdo da página após carregar
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Encontrar todos os contêineres de apartamentos
    container_apartamentos = soup.find_all('div', class_='BaseCard_card__content__pL2Vc w-full p-6')

    for apartamento in container_apartamentos:
        try:
            titulo = apartamento.find('h2',
                                      class_='l-text l-u-color-neutral-28 l-text--variant-heading-small l-text--weight-medium truncate').get_text(
                strip=True)
        except AttributeError:
            titulo = None

        try:
            aluguel = apartamento.find('p',
                                       class_='l-text l-u-color-neutral-28 l-text--variant-heading-small l-text--weight-bold undefined').get_text(
                strip=True).replace('R$', '').replace('.', '').replace('/mês', '').strip()
        except AttributeError:
            aluguel = None

        try:
            endereco = apartamento.find('p',
                                        class_='l-text l-u-color-neutral-28 l-text--variant-body-small l-text--weight-regular truncate').get_text(
                strip=True)
        except AttributeError:
            endereco = None

        try:
            quartos = apartamento.find('p', itemprop='numberOfRooms').get_text(strip=True)
        except AttributeError:
            quartos = None

        try:
            espaco = apartamento.find('p', itemprop='floorSize').get_text(strip=True).replace('m²', '').strip()
        except AttributeError:
            espaco = None

        try:
            banheiros = apartamento.find('p', itemprop='numberOfBathroomsTotal').get_text(strip=True)
        except AttributeError:
            banheiros = None

        try:
            vagas_garagem = apartamento.find('p', itemprop='numberOfParkingSpaces').get_text(strip=True)
        except AttributeError:
            vagas_garagem = None

        # Captura o link para a página do apartamento
        try:
            link = apartamento.find('a', class_='ListingCard_result-card__wrapper__6osq8')['href']
        except TypeError:
            link = None

        # Adiciona a data de coleta
        data_coleta = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d')

        # Adiciona os dados coletados ao dicionário
        dados_apartamentos.append({
            'Título': titulo,
            'Aluguel': aluguel,
            'Quartos': quartos,  # Informação não disponível no exemplo fornecido
            'Espaço': espaco,
            'Banheiros': banheiros,
            'Vagas de Garagem': vagas_garagem,
            'Endereço': endereco,
            'Link': link,
            'Data': data_coleta
        })

    return False  # Indica que não há mais páginas para processar


def main():
    # Configurações do Selenium
    driver = webdriver.Chrome()  # Altere para o caminho correto do chromedriver se necessário
    driver.get("https://www.zapimoveis.com.br/aluguel/imoveis/sp+sao-paulo+zona-sul+itaim-bibi/")

    dados_apartamentos = []

    # Loop para percorrer as páginas e coletar dados
    while True:
        if not coletar_dados_apartamentos_zapimoveis(driver, dados_apartamentos):
            break

    driver.quit()

    # Imprimir ou salvar os dados como desejar
    for dados in dados_apartamentos:
        print(dados)


if __name__ == "__main__":
    main()
