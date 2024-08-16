import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import pytz
from datetime import datetime
import os
from urllib.parse import urljoin

# Função para criar o scraper com rotação de User-Agent
def criar_scraper():
    return cloudscraper.create_scraper()

# Função para coletar dados de apartamentos no Homegate
def coletar_dados_apartamentos_homegate(soup, dados_apartamentos):
    tz = pytz.timezone('Europe/Zurich')
    apartamentos = soup.select("div[role='listitem'][data-test='result-list-item']")

    for apto in apartamentos:
        try:
            titulo = apto.select_one('.HgListingDescription_title_NAAxy span').get_text(strip=True)
            aluguel = apto.select_one('.HgListingCard_price_JoPAs').get_text(strip=True)
            quartos = apto.select_one(
                ".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span:first-child > strong").get_text(strip=True)
            espaco = apto.select(".HgListingRoomsLivingSpace_roomsLivingSpace_GyVgq > span > strong")[1].get_text(
                strip=True)
            endereco = apto.select_one('.HgListingCard_address_JGiFv').get_text(strip=True)
            link = apto.select_one("a.HgCardElevated_link_EHfr7").get('href')

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
            titulo = apto.select_one(".HgListingDescription_title_NAAxy span").get_text(strip=True)
            aluguel = apto.select_one(".HgListingRoomsLivingSpacePrice_price_u9Vee").get_text(strip=True)
            quartos = apto.select_one(
                ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:first-child").get_text(strip=True)
            espaco = apto.select_one(
                ".HgListingRoomsLivingSpacePrice_roomsLivingSpacePrice_M6Ktp > strong:nth-child(3)").get_text(
                strip=True)
            endereco = apto.select_one("div.HgListingCard_address_JGiFv address").get_text(strip=True)
            link = apto.select_one("a.HgCardElevated_link_EHfr7").get('href')

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
            # Converter a URL relativa para absoluta
            url = urljoin(response.url, next_button.get('href'))
            print(f"Mudando para a próxima página: {url}")
            time.sleep(1)  # Aguardar antes de ir para a próxima página
        else:
            print("Botão 'Próxima página' está desabilitado ou não encontrado.")
            break

    return pd.DataFrame(dados_apartamentos)


# Função principal de raspagem que integra tudo
def raspar_dados(site, tipo, cidade):
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

    # Criar a pasta 'dados_brutos' se ela não existir
    pasta_dados_brutos = "dados_brutos"
    os.makedirs(pasta_dados_brutos, exist_ok=True)

    # Salvar o arquivo na pasta 'dados_brutos'
    data_extracao = datetime.now().strftime('%Y%m%d')
    nome_arquivo = f"{site}_{tipo}_{cidade.lower()}_{data_extracao}.xlsx"
    caminho_arquivo = os.path.join(pasta_dados_brutos, nome_arquivo)
    df.to_excel(caminho_arquivo, index=False)
    print(f"Dados salvos em: {caminho_arquivo}")
    return df

# Variável global para controle da raspagem
parar_raspagem = False

def set_parar_raspagem(valor):
    global parar_raspagem
    parar_raspagem = valor

def get_parar_raspagem():
    global parar_raspagem
    return parar_raspagem
