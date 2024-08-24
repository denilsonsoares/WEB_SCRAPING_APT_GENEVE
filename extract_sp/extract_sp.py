import time
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd  # Importa a biblioteca pandas para salvar os dados em Excel


def rolar_pagina_gradualmente(driver, duracao=60, intervalo=0.1):
    # Rola a página gradualmente por 'duracao' segundos com 'intervalo' segundos entre cada rolagem
    tempo_final = time.time() + duracao
    altura_anterior = 0
    incremento = 0.005  # Percentual de rolagem para cada passo

    while time.time() < tempo_final:
        # Rola suavemente para baixo
        driver.execute_script(f"window.scrollBy(0, document.body.scrollHeight * {incremento});")
        time.sleep(intervalo)

        # Verifica a altura atual da página
        altura_atual = driver.execute_script("return window.pageYOffset;")

        # Se a altura atual for igual à altura anterior, significa que não rolou mais
        if altura_atual == altura_anterior:
            # Volta suavemente ao topo da página
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(intervalo * 2)  # Pausa um pouco mais antes de rolar novamente
        else:
            # Atualiza a altura anterior
            altura_anterior = altura_atual

def coletar_dados_apartamentos_zapimoveis(driver, dados_apartamentos):
    rolar_pagina_gradualmente(driver)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    container_apartamentos = soup.find_all('div', class_='BaseCard_card__content__pL2Vc w-full p-6')

    for apartamento in container_apartamentos:
        try:
            titulo = apartamento.find('h2', class_='l-text l-u-color-neutral-28 l-text--variant-heading-small l-text--weight-medium truncate').get_text(strip=True)
        except AttributeError:
            titulo = None

        try:
            aluguel = apartamento.find('p', class_='l-text l-u-color-neutral-28 l-text--variant-heading-small l-text--weight-bold undefined').get_text(strip=True).replace('R$', '').replace('.', '').replace('/mês', '').strip()
        except AttributeError:
            aluguel = None

        try:
            endereco = apartamento.find('p', class_='l-text l-u-color-neutral-28 l-text--variant-body-small l-text--weight-regular truncate').get_text(strip=True)
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

        try:
            link = apartamento.find_parent('a')['href']
            if not link.startswith('http'):
                link = "https://www.zapimoveis.com.br" + link
        except TypeError:
            link = None

        data_coleta = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d %H:%M:%S')

        dados_apartamentos.append({
            'Título': titulo,
            'Aluguel': aluguel,
            'Quartos': quartos,
            'Espaço': espaco,
            'Banheiros': banheiros,
            'Vagas de Garagem': vagas_garagem,
            'Endereço': endereco,
            'Link': link,
            'Data': data_coleta
        })
    for apto in dados_apartamentos:
        print(apto)
    return True

def main():
    # Configurações do navegador com opções para desativar recursos desnecessários
    chrome_options = webdriver.ChromeOptions()
    chrome_prefs = {
        "profile.managed_default_content_settings.images": 2,  # Desativa imagens
        "profile.managed_default_content_settings.stylesheets": 2,  # Desativa CSS
        "profile.managed_default_content_settings.javascript": 1,  # Permite JavaScript, necessário para carregar o HTML
        "profile.managed_default_content_settings.plugins": 2,  # Desativa plugins
        "profile.managed_default_content_settings.popups": 2,  # Desativa popups
        "profile.managed_default_content_settings.geolocation": 2,  # Desativa geolocalização
        "profile.managed_default_content_settings.notifications": 2  # Desativa notificações
    }
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    #chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless (sem GUI)

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.zapimoveis.com.br/aluguel/imoveis/sp+sao-paulo+zona-sul+itaim-bibi/4-quartos/")

    dados_apartamentos = []

    # Loop para percorrer as páginas e coletar dados
    while True:
        coleta_realizada = coletar_dados_apartamentos_zapimoveis(driver, dados_apartamentos)

        # Verifica se o botão de 'Próxima página' está presente e clique nele
        try:
            next_button = driver.find_element(By.XPATH, "//button[@data-testid='next-page']")
            if next_button.is_displayed():
                next_button.click()
                time.sleep(4)  # Aguarda a página carregar
            else:
                break  # Sai do loop se o botão não estiver visível
        except:
            break  # Sai do loop se não houver botão de próxima página

    driver.quit()

    # Salvar os dados coletados em um arquivo Excel
    df = pd.DataFrame(dados_apartamentos)
    df.to_excel('dados_apartamentos.xlsx', index=False)

    print("Dados salvos em 'dados_apartamentos.xlsx'")

if __name__ == "__main__":
    main()
