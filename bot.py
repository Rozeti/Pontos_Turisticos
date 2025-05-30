import time
import urllib.parse
import logging
import sqlite3
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import os
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Configurar logging em português
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='acessibilidade_bot.log',
    encoding='utf-8'
)
logger = logging.getLogger()

# Inicializar geocoder
geolocator = Nominatim(user_agent="acessibilidade_bot")

# Configurar opções do Selenium
def configurar_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Executar em modo headless
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Driver Selenium configurado com sucesso.")
        return driver
    except WebDriverException as e:
        logger.error(f"Erro ao configurar o driver Selenium: {e}")
        return None

# Função para busca avançada de informações de acessibilidade com Selenium
def busca_acessibilidade_web(nome_atracao, driver):
    try:
        info_acessibilidade = {
            'motora': [],
            'visual': [],
            'auditiva': [],
            'cognitiva': [],
            'negativas': []
        }
        palavras_chave = {
            'motora': ['rampa', 'elevador', 'cadeirante', 'acesso adaptado', 'banheiro adaptado', 'acessível', 'mobilidade', 'acesso para deficientes', 'cadeira de rodas', 'estacionamento reservado'],
            'visual': ['piso tátil', 'braille', 'guia visual', 'sinalização tátil', 'tátil', 'deficiência visual', 'sinalização acessível', 'placa em braille'],
            'auditiva': ['intérprete de libras', 'guia auditivo', 'legendas', 'libras', 'deficiência auditiva', 'áudio descrição', 'áudio-guia', 'sinalização sonora'],
            'cognitiva': ['guia simplificado', 'sala sensorial', 'informação clara', 'deficiência cognitiva', 'autismo', 'espaço sensorial', 'material acessível'],
            'negativas': ['sem acessibilidade', 'sem rampa', 'sem elevador', 'inacessível', 'sem piso tátil', 'sem braille', 'sem libras', 'sem guia auditivo', 'sem acesso', 'não acessível']
        }

        # Lista de fontes confiáveis para buscar informações
        fontes = [
            f"https://www.google.com/search?q={urllib.parse.quote(nome_atracao + ' Brasília acessibilidade')}",
            "https://turismo.df.gov.br",
            "https://esporte.df.gov.br",
            "https://www.tripadvisor.com.br",
            f"https://www.google.com/search?q={urllib.parse.quote(nome_atracao + ' Brasília acessibilidade site:jornaldebrasilia.com.br')}",
            f"https://www.google.com/search?q={urllib.parse.quote(nome_atracao + ' Brasília acessibilidade site:arenabsb.com.br')}"
        ]

        sites_institucionais = {
            "Estádio Mané Garrincha": "https://arenabsb.com.br",
            "Congresso Nacional": "https://www.congressonacional.leg.br",
            "Palácio do Planalto": "https://www.gov.br/planalto",
            "Palácio Itamaraty": "https://www.gov.br/mre"
        }

        # Buscar em cada fonte
        for url in fontes:
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                for tipo, palavras in palavras_chave.items():
                    for palavra in palavras:
                        if palavra in page_text:
                            info_acessibilidade[tipo].append(palavra)
            except (TimeoutException, WebDriverException) as e:
                logger.warning(f"Erro ao acessar {url}: {e}")

        # Busca em sites institucionais específicos
        if nome_atracao in sites_institucionais:
            try:
                url_institucional = sites_institucionais[nome_atracao]
                driver.get(url_institucional)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                for tipo, palavras in palavras_chave.items():
                    for palavra in palavras:
                        if palavra in page_text:
                            info_acessibilidade[tipo].append(palavra)
            except (TimeoutException, WebDriverException) as e:
                logger.warning(f"Erro ao acessar site institucional {url_institucional}: {e}")

        # Gerar descrição consolidada mais clara e coesa
        descricao = f"O local '{nome_atracao}' apresenta as seguintes condições de acessibilidade: "
        if info_acessibilidade['motora']:
            recursos = ', '.join(set(info_acessibilidade['motora']))
            descricao += f"Para acessibilidade motora, há recursos como {recursos}, que facilitam o acesso para pessoas com mobilidade reduzida, como cadeirantes ou usuários de bengalas. "
        else:
            descricao += "Não foram encontradas informações específicas sobre acessibilidade motora, o que pode indicar limitações para pessoas com mobilidade reduzida. "
        if info_acessibilidade['visual']:
            recursos = ', '.join(set(info_acessibilidade['visual']))
            descricao += f"Para acessibilidade visual, estão disponíveis {recursos}, que auxiliam pessoas com deficiência visual, como cegos ou com baixa visão. "
        else:
            descricao += "Não há informações específicas sobre acessibilidade visual, o que pode dificultar a experiência de pessoas com deficiência visual. "
        if info_acessibilidade['auditiva']:
            recursos = ', '.join(set(info_acessibilidade['auditiva']))
            descricao += f"Para acessibilidade auditiva, o local oferece {recursos}, que apoiam pessoas com deficiência auditiva, como surdos ou com audição reduzida. "
        else:
            descricao += "Não foram encontradas informações sobre acessibilidade auditiva, podendo haver barreiras para pessoas com deficiência auditiva. "
        if info_acessibilidade['cognitiva']:
            recursos = ', '.join(set(info_acessibilidade['cognitiva']))
            descricao += f"Para acessibilidade cognitiva, há {recursos}, que ajudam pessoas com deficiência cognitiva, como autismo ou dificuldades de compreensão, a utilizar o espaço. "
        else:
            descricao += "Não há informações específicas sobre acessibilidade cognitiva, o que pode limitar a acessibilidade para pessoas com necessidades cognitivas. "
        if info_acessibilidade['negativas']:
            recursos = ', '.join(set(info_acessibilidade['negativas']))
            descricao += f"Foram identificadas limitações, como {recursos}, que podem impactar a acessibilidade geral do local."

        return descricao.strip(), info_acessibilidade
    except Exception as e:
        logger.error(f"Erro na busca de acessibilidade para {nome_atracao}: {e}")
        return f"Não foram encontradas informações detalhadas de acessibilidade para '{nome_atracao}'.", info_acessibilidade

# Função para coletar informações do local
def coletar_info_local(nome_atracao, driver):
    try:
        # Buscar informações de acessibilidade
        descricao, info_acessibilidade = busca_acessibilidade_web(nome_atracao, driver)

        # Geocodificar a atração
        localizacao = None
        try:
            localizacao = geolocator.geocode(f"{nome_atracao}, Brasília, DF, Brasil", timeout=10)
        except Exception as e:
            logger.error(f"Erro ao geocodificar {nome_atracao}: {e}")

        if localizacao:
            return {
                'nome': nome_atracao,
                'info_acessibilidade': descricao,
                'info_raw': info_acessibilidade,
                'latitude': localizacao.latitude,
                'longitude': localizacao.longitude
            }
        else:
            logger.warning(f"Não foi possível geocodificar {nome_atracao}.")
            return {
                'nome': nome_atracao,
                'info_acessibilidade': descricao,
                'info_raw': info_acessibilidade,
                'latitude': None,
                'longitude': None
            }
    except Exception as e:
        logger.error(f"Erro ao coletar dados de {nome_atracao}: {e}")
        return {
            'nome': nome_atracao,
            'info_acessibilidade': "Não foram encontradas informações detalhadas de acessibilidade.",
            'info_raw': {'motora': [], 'visual': [], 'auditiva': [], 'cognitiva': [], 'negativas': []},
            'latitude': None,
            'longitude': None
        }

# Função para criar banco de dados SQLite
def criar_banco_dados():
    try:
        conn = sqlite3.connect('acessibilidade_brasilia.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS atracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                info_acessibilidade TEXT,
                latitude REAL,
                longitude REAL,
                classificacao TEXT
            )
        ''')
        cursor.execute('DELETE FROM atracoes')  # Limpar tabela antes de inserir novos dados
        conn.commit()
        logger.info("Banco de dados e tabela criados/limpos com sucesso.")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Erro no banco de dados: {e}")
        return None

# Função para classificar acessibilidade de forma profissional
def classificar_acessibilidade(info_raw):
    # Contar tipos de acessibilidade presentes
    tipos_acessiveis = 0
    if info_raw['motora']:
        tipos_acessiveis += 1
    if info_raw['visual']:
        tipos_acessiveis += 1
    if info_raw['auditiva']:
        tipos_acessiveis += 1
    if info_raw['cognitiva']:
        tipos_acessiveis += 1

    # Verificar presença de palavras negativas
    contagem_negativa = len(info_raw['negativas'])

    # Critérios baseados na NBR 9050 e relatos reais
    if tipos_acessiveis >= 3 and contagem_negativa == 0:
        return "Acessível"
    elif tipos_acessiveis >= 1 and contagem_negativa == 0:
        return "Parcialmente Acessível"
    elif contagem_negativa > 0:
        return "Não Acessível"
    else:
        return "Não Acessível"

# Função para armazenar dados no banco
def armazenar_dados(conn, dados):
    try:
        cursor = conn.cursor()
        for item in dados:
            if item:
                classificacao = classificar_acessibilidade(item['info_raw'])
                try:
                    cursor.execute('''
                        INSERT INTO atracoes (nome, info_acessibilidade, latitude, longitude, classificacao)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (item['nome'], item['info_acessibilidade'], item['latitude'], item['longitude'], classificacao))
                except sqlite3.IntegrityError:
                    logger.warning(f"Entrada duplicada para {item['nome']}. Ignorando.")
        conn.commit()
        logger.info("Dados armazenados com sucesso.")
    except sqlite3.Error as e:
        logger.error(f"Erro ao armazenar dados: {e}")

# Função para criar mapa interativo com popups ajustados
def criar_mapa_interativo(conn):
    try:
        # Ler dados do banco
        df = pd.read_sql_query("SELECT * FROM atracoes", conn)
        
        if df.empty:
            logger.warning("Nenhum dado encontrado no banco para plotar no mapa.")
            return None

        # Criar mapa centrado em Brasília
        m = folium.Map(location=[-15.7942, -47.8825], zoom_start=12, tiles='OpenStreetMap')
        marker_cluster = MarkerCluster().add_to(m)

        # Mapa de cores para classificações
        mapa_cores = {
            "Acessível": "green",
            "Não Acessível": "red",
            "Parcialmente Acessível": "orange",
            "Desconhecido": "gray"
        }

        # Adicionar marcadores com popups ajustados
        for _, row in df.iterrows():
            if row['latitude'] is None or row['longitude'] is None:
                logger.warning(f"Coordenadas ausentes para {row['nome']}. Ignorando marcador.")
                continue
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 300px; padding: 10px;">
                <h3 style="margin: 0; color: {mapa_cores.get(row['classificacao'], 'gray')}; font-size: 18px;">
                    {row['nome']}
                </h3>
                <hr style="margin: 5px 0; border-color: #ccc;">
                <p style="font-size: 14px; margin: 5px 0;">
                    <strong>Classificação Geral:</strong> {row['classificacao']}
                </p>
                <h4 style="margin: 10px 0 5px; color: #333; font-size: 16px;">Detalhes de Acessibilidade</h4>
                <p style="font-size: 14px; margin: 0; line-height: 1.5;">
                    {row['info_acessibilidade']}
                </p>
            </div>
            """
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_html, max_width=350),
                icon=folium.Icon(color=mapa_cores.get(row['classificacao'], 'gray'))
            ).add_to(marker_cluster)

        # Salvar mapa em HTML
        mapa_path = 'mapa_acessibilidade_brasilia.html'
        m.save(mapa_path)
        logger.info(f"Mapa interativo criado e salvo como '{mapa_path}'.")
        return mapa_path
    except Exception as e:
        logger.error(f"Erro ao criar mapa: {e}")
        return None

# Função principal
def main():
    # Configurar o driver Selenium
    driver = configurar_driver()
    if not driver:
        print("Erro ao configurar o driver Selenium. Verifique o log para mais detalhes.")
        return

    try:
        # Solicitar o ponto turístico ao usuário
        ponto_turistico = input("Digite o nome do ponto turístico que deseja pesquisar (ex.: Estádio Mané Garrincha): ").strip()

        if not ponto_turistico:
            print("Por favor, digite um nome válido para o ponto turístico.")
            return

        # Criar o banco de dados
        conn = criar_banco_dados()
        if not conn:
            print("Erro ao criar o banco de dados. Verifique o log para mais detalhes.")
            return

        # Coletar informações do local
        print(f"Coletando informações de acessibilidade para '{ponto_turistico}'...")
        resultado = coletar_info_local(ponto_turistico, driver)
        if not resultado:
            print(f"Não foi possível coletar informações para '{ponto_turistico}'.")
            conn.close()
            return

        # Armazenar os dados no banco
        armazenar_dados(conn, [resultado])

        # Criar e abrir o mapa interativo
        print("Gerando o mapa interativo...")
        mapa_path = criar_mapa_interativo(conn)
        if mapa_path:
            mapa_path_absolute = os.path.abspath(mapa_path)
            mapa_url = f"file:///{mapa_path_absolute.replace(os.sep, '/')}"
            print(f"Mapa gerado com sucesso! Tentando abrir '{mapa_path}' no Google Chrome...")

            try:
                chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
                webbrowser.register('chrome', None, webbrowser.GenericBrowser(chrome_path))
                webbrowser.get('chrome').open(mapa_url)
            except Exception as e:
                print(f"Erro ao abrir o mapa automaticamente: {e}")
                print(f"Por favor, abra o arquivo manualmente em: {mapa_path_absolute}")
        else:
            print("Não foi possível gerar o mapa. Verifique o log para mais detalhes.")

        # Fechar a conexão com o banco
        conn.close()
        logger.info("Conexão com o banco de dados fechada.")
    finally:
        # Fechar o driver Selenium
        driver.quit()
        logger.info("Driver Selenium encerrado.")

if __name__ == "__main__":
    main()
