from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests
import time
import sqlite3

# PALAVRAS-CHAVE por acessibilidade
CHAVES = {
    "rampa": ["rampa", "acesso sem degraus"],
    "banheiro_adaptado": ["banheiro adaptado", "acessível para cadeirantes"],
    "sinalizacao_visual": ["sinalização tátil", "piso tátil", "braile"],
    "audiodescricao": ["áudio descrição", "informações sonoras"]
}

def init_driver():
    options = Options()
    options.add_argument('--headless')  # Roda sem abrir o navegador
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Aqui está a correção que funciona com Selenium 4.6+
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def buscar_links(driver, termo):
    print(f"Pesquisando no DuckDuckGo por: {termo}")
    driver.get(f"https://duckduckgo.com/?q={termo}+acessibilidade&t=h_&ia=web")

    try:
        # Aguarda até que os resultados apareçam (tempo máximo: 10 segundos)
        elementos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-testid='result-title-a']"))
        )
        links = [e.get_attribute("href") for e in elementos[:3]]
        return links

    except:
        print("⚠️ Nenhum resultado encontrado ou a página demorou demais para carregar.")
        return []

def extrair_texto(url):
    print(f"Extraindo conteúdo de: {url}")
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        return ' '.join([p.text for p in soup.find_all('p')])
    except:
        return ""

def classificar(texto):
    resultado = {k: False for k in CHAVES}
    for k, palavras in CHAVES.items():
        for palavra in palavras:
            if palavra.lower() in texto.lower():
                resultado[k] = True
    return resultado

def salvar(nome, lat, lon, texto, classificacao):
    conn = sqlite3.connect('acessibilidade_turismo.db')
    c = conn.cursor()

    c.execute("INSERT INTO ponto_turistico (nome, latitude, longitude, descricao) VALUES (?, ?, ?, ?)",
              (nome, lat, lon, texto[:200]))

    ponto_id = c.lastrowid

    c.execute('''
        INSERT INTO acessibilidade (
            ponto_id, rampa, banheiro_adaptado, sinalizacao_visual, audiodescricao, observacoes, origem
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ponto_id,
        classificacao['rampa'],
        classificacao['banheiro_adaptado'],
        classificacao['sinalizacao_visual'],
        classificacao['audiodescricao'],
        texto[:500],
        'Web scraping Google'
    ))

    conn.commit()
    conn.close()
    print(f"{nome} salvo no banco de dados com sucesso.")

def executar_bot():
    driver = init_driver()
    nome_local = "Catedral de Brasília"
    latitude, longitude = -15.7983, -47.8750

    links = buscar_links(driver, nome_local)
    print("Links encontrados:", links)

    for link in links:
        texto = extrair_texto(link)
        print("Texto extraído (resumo):", texto[:300])  # Mostra trecho do texto

        if texto:
            classificacao = classificar(texto)
            print("Classificação:", classificacao)
            salvar(nome_local, latitude, longitude, texto, classificacao)
            break
        else:
            print("Não foi possível extrair texto útil do link:", link)

    driver.quit()


if __name__ == "__main__":
    executar_bot()
