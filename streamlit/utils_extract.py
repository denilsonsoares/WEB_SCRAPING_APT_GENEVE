import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import pytz
from datetime import datetime
import os
from urllib.parse import urljoin
import pandas as pd
import os
from openpyxl import Workbook

# Função para salvar dados em formato Excel, linha por linha, ignorando linhas problemáticas
from openpyxl import Workbook
from openpyxl.utils.exceptions import IllegalCharacterError
import os

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

            aluguel_element = apto.select_one('.HgListingCard_price_JoPAs')
            aluguel = aluguel_element.get_text(strip=True) if aluguel_element else 'N/A'

            quartos_element = apto.select_one(".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:first-child > strong")
            quartos = quartos_element.get_text(strip=True) if quartos_element else 'N/A'

            espaco_elements = apto.select(".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span > strong")
            espaco = espaco_elements[1].get_text(strip=True) if len(espaco_elements) > 1 else 'N/A'

            endereco_element = apto.select_one('.HgListingCard_address_JGiFv')
            endereco = endereco_element.get_text(strip=True) if endereco_element else 'N/A'

            link_element = apto.select_one("a.HgCardElevated_link_EHfr7")
            link = ("https://www.homegate.ch"+link_element.get('href')) if link_element else 'N/A'

            data_extracao = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

            dados_apartamentos.append({
                'Título': titulo,
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })

            print(
                f"Título: {titulo}, Aluguel: {aluguel}, Quartos: {quartos}, Espaço: {espaco}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
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
                aluguel_element = apto.select_one(".HgListingRoomsLivingSpacePrice_price_u9Vee")
                aluguel = aluguel_element.get_text(strip=True) if aluguel_element else 'N/A'
            except Exception as e:
                aluguel = 'N/A'
                print(f"Erro ao extrair o aluguel: {str(e)}")

            try:
                quartos_element = apto.select_one(".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:first-child")
                quartos = quartos_element.get_text(strip=True) if quartos_element else 'N/A'
            except Exception as e:
                quartos = 'N/A'
                print(f"Erro ao extrair a quantidade de quartos: {str(e)}")

            try:
                espaco_element = apto.select_one(".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:nth-child(3)")
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
                'Aluguel': aluguel,
                'Quartos': quartos,
                'Espaço': espaco,
                'Endereço': endereco,
                'Link': link,
                'Data': data_extracao
            })

            print(
                f"Título: {titulo}, Aluguel: {aluguel}, Quartos: {quartos}, Espaço: {espaco}, Endereço: {endereco}, Link: {link}, Data de Extração: {data_extracao}")
            print("-" * 40)

        except Exception as e:
            print(f"Erro ao coletar dados do apartamento: {str(e)}")
            continue


# Função genérica para navegar pelas páginas e coletar dados
def navegar_paginas(scraper, url, site):
    dados_apartamentos = []

    while not get_parar_raspagem():
        try:
            response = scraper.get(url)
            if response.status_code != 200:
                print(f"Falha ao acessar a página: Status Code {response.status_code}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')

            if site == "homegate":
                coletar_dados_apartamentos_homegate(soup, dados_apartamentos)
            elif site == "immoscout24":
                coletar_dados_apartamentos_immoscout(soup, dados_apartamentos)

            next_button = soup.select_one("a[aria-label='Go to next page']")
            if next_button and next_button.get('href'):
                url = urljoin(response.url, next_button.get('href'))
                print(f"Mudando para a próxima página: {url}")
                time.sleep(1)
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

        scraper = criar_scraper()
        df = navegar_paginas(scraper, url, site)

        pasta_dados_brutos = "dados_brutos"
        os.makedirs(pasta_dados_brutos, exist_ok=True)

        data_extracao = datetime.now().strftime('%Y%m%d')
        nome_arquivo = f"{site}_{tipo}_{cidade.lower()}_{data_extracao}.xlsx"
        #caminho_arquivo = os.path.join(pasta_dados_brutos, nome_arquivo)
        #df.to_excel(caminho_arquivo, index=False)
        #print(f"Dados salvos em: {caminho_arquivo}")

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
