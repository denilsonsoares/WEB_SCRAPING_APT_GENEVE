
from selenium.webdriver.common.by import By
import cloudscraper
from bs4 import BeautifulSoup
import time
import pytz
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError
import os

# Função para salvar dados em formato Excel, linha por linha, ignorando linhas problemáticas
def salvar_dados(df, pasta_dados_brutos, nome_arquivo):
    caminho_excel = os.path.join(pasta_dados_brutos, nome_arquivo)

    # Cria um novo Workbook para salvar os dados
    wb = Workbook()
    ws = wb.active

    # Adiciona os cabeçalhos na primeira linha
    ws.append(df.columns.tolist())

    # Itera sobre as linhas do DataFrame
    for idx, row in df.iterrows():
        try:
            # Verifica e trata possíveis caracteres ilegais em cada célula
            cleaned_row = []
            for cell in row.tolist():
                if isinstance(cell, str):
                    # Remove caracteres não imprimíveis
                    cleaned_cell = ''.join(c for c in cell if c.isprintable())
                    cleaned_row.append(cleaned_cell)
                else:
                    cleaned_row.append(cell)

            # Adiciona a linha tratada no arquivo Excel
            ws.append(cleaned_row)

        except IllegalCharacterError as e:
            # Se ocorrer um erro específico de caracteres ilegais, ignora a linha
            print(f"Erro ao salvar linha {idx}: {str(e)} - Linha ignorada.")
        except Exception as e:
            # Se ocorrer qualquer outro erro, imprime a linha problemática e continua
            print(f"Erro inesperado na linha {idx}: {str(e)} - Linha ignorada.")

    # Salva o arquivo Excel
    wb.save(caminho_excel)
    print(f"Dados salvos em formato Excel: {caminho_excel}")

# Função para criar o scraper com rotação de User-Agent
def criar_scraper():
    return cloudscraper.create_scraper()

# Função para coletar dados de apartamentos no Homegate
def coletar_dados_apartamentos_homegate(soup, dados_apartamentos):
    tz = pytz.timezone('Europe/Zurich')
    apartamentos = soup.select("div[role='listitem'][data-test='result-list-item']")

    for apto in apartamentos:
        try:
            titulo_element = apto.select_one('.HgListingDescription_title_NAAxy span')
            titulo = titulo_element.get_text(strip=True) if titulo_element else 'N/A'

            preco_element = apto.select_one('.HgListingCard_price_JoPAs')
            preco = preco_element.get_text(strip=True) if preco_element else 'N/A'

            try:
                # Tenta encontrar o elemento de quartos (rooms)
                quartos_element = apto.select_one(
                    ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:first-child > strong")
                quartos = quartos_element.get_text(
                    strip=True) if quartos_element and 'rooms' in quartos_element.find_parent(
                    'span').get_text() else 'N/A'
            except Exception as e:
                quartos = 'N/A'
                print(f"Erro ao extrair quartos: {e}")

            try:
                # Tenta encontrar o elemento de espaço de vida (living space)
                espaco_element = apto.select_one(
                    ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:last-child > strong")
                espaco = espaco_element.get_text(
                    strip=True) if espaco_element and 'living space' in espaco_element.find_parent(
                    'span').get_text() else 'N/A'
            except Exception as e:
                espaco = 'N/A'
                print(f"Erro ao extrair espaço de vida: {e}")

            endereco_element = apto.select_one('.HgListingCard_address_JGiFv')
            endereco = endereco_element.get_text(strip=True) if endereco_element else 'N/A'

            link_element = apto.select_one("a.HgCardElevated_link_EHfr7")
            link = ("https://www.homegate.ch"+link_element.get('href')) if link_element else 'N/A'

            data_extracao = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            dados_apartamentos.append({
                'Título': titulo,
                'Preço (CHF)': preco,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })

            print(
                f"Título: {titulo}, Preço: {preco}, Quartos: {quartos}, Espaço: {espaco}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue

# Função para coletar dados de apartamentos no ImmoScout24
def coletar_dados_apartamentos_immoscout(soup, dados_apartamentos):
    tz = pytz.timezone('Europe/Zurich')
    apartamentos = soup.select("div[role='listitem'][data-test='result-list-item']")

    for apto in apartamentos:
        try:
            titulo_element = apto.select_one(".HgListingDescription_title_NAAxy span")
            titulo = titulo_element.get_text(strip=True) if titulo_element else 'N/A'

            try:
                # Tenta extrair o preço
                preco_element = apto.select_one(".HgListingRoomsLivingSpacePrice_price_u9Vee")
                preco = preco_element.get_text(strip=True) if preco_element else 'N/A'
            except Exception as e:
                preco = 'N/A'
                print(f"Erro ao extrair o preço: {str(e)}")

            try:
                # Tenta extrair a quantidade de quartos
                quartos_element = apto.select_one(
                    ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:first-child")
                quartos = quartos_element.get_text(
                    strip=True) if quartos_element and 'rooms' in quartos_element.get_text() else 'N/A'
            except Exception as e:
                quartos = 'N/A'
                print(f"Erro ao extrair a quantidade de quartos: {str(e)}")

            try:
                # Tenta extrair o espaço de vida
                espaco_element = apto.select_one(
                    ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong[title='living space']")
                espaco = espaco_element.get_text(strip=True) if espaco_element else 'N/A'
            except Exception as e:
                espaco = 'N/A'
                print(f"Erro ao extrair o espaço de vida: {str(e)}")


            endereco_element = apto.select_one("div.HgListingCard_address_JGiFv address")
            endereco = endereco_element.get_text(strip=True) if endereco_element else 'N/A'

            link_element = apto.select_one("a.HgCardElevated_link_EHfr7")
            link = ("https://www.immoscout24.ch"+link_element.get('href')) if link_element else 'N/A'

            data_extracao = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            dados_apartamentos.append({
                'Título': titulo,
                'Preço (CHF)': preco,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })

            print(
                f"Título: {titulo}, Preço: {preco}, Quartos: {quartos}, Espaço: {espaco}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue

"""-----------------------------------------------------------------------------"""


# Função para simular a rolagem até o final da página
def rolar_ate_final(scraper, url, headers):
    while True:
        response = scraper.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Verifica se há um botão para carregar mais conteúdo ou se a página chegou ao final
        next_button = soup.find('a', {'aria-label': 'Próxima página'})

        if next_button:
            next_url = next_button['href']
            url = urljoin(url, next_url)
            time.sleep(2)  # Aguarda o carregamento da próxima página
        else:
            break

        yield soup

# Função para coletar dados de apartamentos de ZAP Imóveis
def coletar_dados_apartamentos_zapimoveis(soup, dados_apartamentos):
    container = soup.find('div', class_='listing-wrapper__content')
    if container:
        cards = container.find_all('div', class_='BaseCard_card__content__pL2Vc')
        for card in cards:
            dados_apartamento = extrair_dados_apartamento(card)
            dados_apartamentos.append(dados_apartamento)

# Função de raspagem de dados de ZAP Imóveis
def extrair_dados_apartamento(card):
    try:
        bairro = card.find('h2', {'data-cy': 'rp-cardProperty-location-txt'}).text.strip()
    except:
        bairro = 'N/A'

    try:
        endereco = card.find('p', {'data-cy': 'rp-cardProperty-street-txt'}).text.strip()
    except:
        endereco = 'N/A'

    try:
        descricao = card.find('p', {'class': 'ListingCard_card__description__slBTG'}).text.strip()
    except:
        descricao = 'N/A'

    try:
        area = card.find('p', {'data-cy': 'rp-cardProperty-propertyArea-txt'}).text.strip()
    except:
        area = 'N/A'

    try:
        banheiros = card.find('p', {'data-cy': 'rp-cardProperty-bathroomQuantity-txt'}).text.strip()
    except:
        banheiros = 'N/A'

    try:
        vagas = card.find('p', {'data-cy': 'rp-cardProperty-parkingSpacesQuantity-txt'}).text.strip()
    except:
        vagas = 'N/A'

    try:
        preco = card.find('p', {'data-cy': 'rp-cardProperty-price-txt'}).text.strip()
    except:
        preco = 'N/A'

    return {
        'Bairro': bairro,
        'Endereco': endereco,
        'Descricao': descricao,
        'Area': area,
        'Banheiros': banheiros,
        'Vagas': vagas,
        'Preco': preco
    }
"""-----------------------------------------------------------------------------"""
# Função genérica para navegar pelas páginas e coletar dados
def navegar_paginas(scraper, url, site):
    dados_apartamentos = []

    while not get_parar_raspagem():
        try:
            # Fazendo a requisição HTTP
            response = scraper.get(url)
            if response.status_code != 200:
                print(f"Falha ao acessar a página: Status Code {response.status_code}")
                break

            # Parseando o conteúdo da página
            soup = BeautifulSoup(response.content, 'html.parser')

            # Coletando os dados com base no site
            if site == "homegate":
                coletar_dados_apartamentos_homegate(soup, dados_apartamentos)
            elif site == "immoscout24":
                coletar_dados_apartamentos_immoscout(soup, dados_apartamentos)
            elif site == "zapimoveis":
                coletar_dados_apartamentos_zapimoveis(soup, dados_apartamentos)

            # Identificação do botão de próxima página
            if site == "zapimoveis":
                next_button = soup.select_one('button[data-testid="next-page"]')
                if next_button:
                    # Aqui tentamos simular um clique ou seguir para a próxima página
                    print("Botão 'Próxima página' encontrado.")
                    # Neste ponto, sem Selenium, seria necessário verificar se há uma URL a ser extraída.
                    # Se o botão usa JavaScript para carregar a próxima página, o scraping não vai funcionar
                    # Se houver um link que o botão aciona, tente capturá-lo e seguir a nova URL
                    # url = urljoin(response.url, ...)
                    print("Mudando para a próxima página: Implementação depende de como a navegação é feita.")
                    time.sleep(1)
                else:
                    print("Botão 'Próxima página' está desabilitado ou não encontrado.")
                    break
            else:
                next_button = soup.select_one("a[aria-label='Go to next page']")
                if next_button:
                    url = urljoin(response.url, next_button.get('href'))
                    print(f"Mudando para a próxima página: {url}")
                    time.sleep(1)  # Aguarda um pouco antes de carregar a próxima página
                else:
                    print("Botão 'Próxima página' está desabilitado ou não encontrado.")
                    break

        except Exception as e:
            print(f"Erro durante a navegação das páginas: {str(e)}")
            break

    return pd.DataFrame(dados_apartamentos)


# Função principal de raspagem que integra tudo
def raspar_dados(site, tipo, cidade):
    try:
        if site == "homegate":
            if cidade == "Geneve":
                if tipo == "alugar":
                    url = "https://www.homegate.ch/rent/apartment/canton-geneva/matching-list"
                elif tipo == "comprar":
                    url = "https://www.homegate.ch/buy/apartment/canton-geneva/matching-list"
            elif cidade == "Zurich":
                if tipo == "alugar":
                    url = "https://www.homegate.ch/rent/real-estate/city-zurich/matching-list"
                elif tipo == "comprar":
                    url = "https://www.homegate.ch/buy/apartment/canton-zurich/matching-list"

        elif site == "immoscout24":
            if cidade == "Geneve":
                if tipo == "alugar":
                    url = "https://www.immoscout24.ch/en/real-estate/rent/canton-geneva"
                elif tipo == "comprar":
                    url = "https://www.immoscout24.ch/en/real-estate/buy/canton-geneva"
            elif cidade == "Zurich":
                if tipo == "alugar":
                    url = "https://www.immoscout24.ch/en/real-estate/rent/city-zuerich"
                elif tipo == "comprar":
                    url = "https://www.immoscout24.ch/en/real-estate/buy/canton-zurich"
        #RASPAR SÃO PAULO:
        elif site == "zapimoveis":
            if cidade == "sao-paulo" and tipo == "alugar":
                url = "https://www.zapimoveis.com.br/aluguel/imoveis/sp+sao-paulo+zona-sul+itaim-bibi/"

        scraper = criar_scraper()
        # Inicialização do WebDriver para Selenium
        df = navegar_paginas(scraper, url, site)
        # Fechamento do WebDriver
        pasta_dados_brutos = "dados_brutos"
        os.makedirs(pasta_dados_brutos, exist_ok=True)

        data_extracao = datetime.now().strftime('%Y%m%d')
        nome_arquivo = f"{site}_{tipo}_{cidade.lower()}_{data_extracao}.xlsx"

        # Usando a função de salvamento
        salvar_dados(df, pasta_dados_brutos, nome_arquivo)

        return df

    except Exception as e:
        print(f"Erro durante a raspagem dos dados: {str(e)}")
        return pd.DataFrame()

# Variável global para controle da raspagem
parar_raspagem = False

def set_parar_raspagem(valor):
    global parar_raspagem
    parar_raspagem = valor

def get_parar_raspagem():
    global parar_raspagem
    return parar_raspagem
