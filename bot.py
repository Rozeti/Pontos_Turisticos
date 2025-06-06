import json
import time
import re
import html
import os
import logging
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim
import folium

# Configurações globais
TIMEOUT = 30
MAX_RELEVANT_SNIPPETS = 15
CONTEXT_WINDOW = 200

# Configuração de logging (apenas console)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Sistema de Recursos de Acessibilidade (atualizado para plataforma)
ACCESSIBILITY_FEATURES = {
    'rampas': {
        'pattern': re.compile(
            r'\b(rampa[s]?|acesso[s]? (sem degrau[s]?|nivelado[s]?|por rampa|para mobilidade reduzida|com corrimão|PCD)|inclina[çc][ãa]o acess[íi]vel)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'mobilidade'
    },
    'elevadores': {
        'pattern': re.compile(
            r'\b(elevador[es]?|elevador[es]? (acess[íi]ve[lis]?|adaptado[s]?|para cadeirante[s]?|com braille|com voz|PCD|de acesso|com porta larga)|acesso por elevador)\b',
            re.IGNORECASE
        ),
        'weight': 3,
        'category': 'mobilidade'
    },
    'banheiros_adaptados': {
        'pattern': re.compile(
            r'\b(banheiro[s]?|sanit[áa]rio[s]?|lavabo[s]?)( (adaptado[s]?|acess[íi]ve[lis]?|para cadeirante[s]?|com barras|PCD))?\b',
            re.IGNORECASE
        ),
        'weight': 3,
        'category': 'mobilidade'
    },
    'plataformas_elevatorias': {
        'pattern': re.compile(
            r'\b(plataforma[s]?|plataforma[s]? (elevat[óo]ria[s]?|de acesso|acess[íi]ve[lis]?|para cadeirante[s]?|PCD)|elevador[es]? de plataforma)\b',
            re.IGNORECASE
        ),
        'weight': 3,
        'category': 'mobilidade'
    },
    'pisos_tateis': {
        'pattern': re.compile(
            r'\b(piso[s]? t[áa]te[lis]?|piso[s]? podot[áa]te[lis]?|sinaliza[çc][ãa]o t[áa]til no piso|caminho[s]? t[áa]til)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'visual'
    },
    'braille': {
        'pattern': re.compile(
            r'\b(braille|braile|sinaliza[çc][ãa]o em braille|placa[s]? em braille|informa[çc][õo]es em braille|legenda[s]? em braille)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'visual'
    },
    'painel_tatil': {
        'pattern': re.compile(
            r'\b(pain[eé]is? t[áa]te[lis]?|maquete[s]? t[áa]til|placa[s]? t[áa]til|mapa[s]? t[áa]til)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'visual'
    },
    'recursos_auditivos': {
        'pattern': re.compile(
            r'\b(sinaliza[çc][ãa]o sonora|audioguia[s]?|[áa]udio descritivo|sistema de [áa]udio acess[íi]vel|loop auditivo)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'auditiva'
    },
    'legendas': {
        'pattern': re.compile(
            r'\b(legenda[s]? (para surdo[s]?|descritiva[s]?|em tempo real|acess[íi]ve[lis]?|em v[íi]deo)|closed caption[s]?|subt[íi]tulo[s]? acess[íi]ve[lis]?)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'auditiva'
    },
    'libras': {
        'pattern': re.compile(
            r'\b((informa[çc][õo]es|v[íi]deo[s]?|atendimento|sinaliza[çc][ãa]o|tradu[çc][ãa]o) em libras|int[ée]rprete[s]? de libras)\b',
            re.IGNORECASE
        ),
        'weight': 3,
        'category': 'auditiva'
    },
    'vagas_especiais': {
        'pattern': re.compile(
            r'\b(vaga[s]? (especial[es]?|para deficiente[s]?|priorit[áa]ria[s]?|PCD)|estacionamento acess[íi]vel)\b',
            re.IGNORECASE
        ),
        'weight': 1,
        'category': 'geral'
    },
    'acesso_universal': {
        'pattern': re.compile(
            r'\b(acesso universal|acessibilidade (total|inclusiva)|desenho universal|ambiente sem barreira[s]?)\b',
            re.IGNORECASE
        ),
        'weight': 3,
        'category': 'geral'
    },
    'acessibilidade_digital': {
        'pattern': re.compile(
            r'\b(acessibilidade digital|site acess[íi]vel|compatibilidade com leitor de tela|WCAG [0-9.]+|contraste elevado)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'digital'
    },
    'recursos_cognitivos': {
        'pattern': re.compile(
            r'\b(sinaliza[çc][ãa]o simplificada|instru[çc][õo]es claras|guia[s]? simplificado[s]?|pictogramas acess[íi]veis|linguagem simples)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'cognitiva'
    },
    'assentos_acessiveis': {
        'pattern': re.compile(
            r'\b(assento[s]? (acess[íi]ve[lis]?|reservado[s]?|priorit[áa]rio[s]?|para cadeirante[s]?|PCD)|espa[çc]o para cadeirante[s]?)\b',
            re.IGNORECASE
        ),
        'weight': 2,
        'category': 'geral'
    }
}

# Palavras-chave de contexto
CONTEXT_KEYWORDS = [
    'acess', 'deficiente', 'cadeirante', 'visual', 'auditi', 'surdo', 'PCD', 'inclus',
    'mobilidade', 'tátil', 'braille', 'libras', 'adaptado', 'acessibilidade', 'universal',
    'facilidade', 'deficiência', 'barreira', 'inclusão', 'acesso', 'especial'
]

def setup_driver():
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4472.124 Safari/537.36")
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        return driver
    except Exception as e:
        logger.error(f"Erro ao configurar driver: {e}")
        raise

def read_tourist_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            landmarks = []
            for line in file:
                if '|' in line:
                    parts = [p.strip() for p in line.strip().split('|') if p.strip()]
                    if len(parts) >= 2:
                        landmarks.append({
                            'name': parts[0],
                            'sources': parts[1:]
                        })
            logger.info(f"Carregados {len(landmarks)} pontos turísticos de {file_path}")
            return landmarks
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {file_path}: {e}")
        return []

def extract_relevant_content(text, source):
    relevant_items = []
    text = text.lower()
    matched_terms = {}

    for feature, data in ACCESSIBILITY_FEATURES.items():
        matched_terms[feature] = set()
        pattern = data['pattern']
        weight = data['weight']
        category = data['category']
        matches = pattern.finditer(text)
        
        for match in matches:
            term = match.group(0).lower()
            start = max(0, match.start() - CONTEXT_WINDOW)
            end = min(len(text), match.end() + CONTEXT_WINDOW)
            snippet = text[start:end].strip()
            
            # Validação de contexto
            has_context = any(keyword.lower() in snippet for keyword in CONTEXT_KEYWORDS)
            if not has_context:
                implicit_context = (
                    feature in ['elevadores', 'banheiros_adaptados', 'rampas', 'plataformas_elevatorias'] and
                    any(word in snippet for word in ['acesso', 'disponível', 'instalado', 'equipado'])
                )
                if not implicit_context:
                    logger.debug(f"Termo rejeitado por falta de contexto: {term} (Feature: {feature}, Snippet: {snippet[:50]}...)")
                    continue
            
            # Normalização para deduplicação
            normalized_term = re.sub(r'\s+', ' ', term).strip()
            normalized_term = re.sub(r's\b', '', normalized_term).strip()
            
            # Permite variações distintas
            term_key = f"{feature}:{normalized_term}"
            if term_key not in matched_terms[feature]:
                matched_terms[feature].add(term_key)
                snippet = html.unescape(snippet)
                snippet = ' '.join(snippet.split())
                
                relevant_items.append({
                    'feature': feature,
                    'term': term,
                    'snippet': snippet,
                    'weight': weight,
                    'category': category,
                    'source': source
                })
                logger.info(f"Recurso identificado: {feature} - Termo: {term} (Fonte: {source})")
            else:
                logger.debug(f"Termo duplicado ignorado: {term} para {feature}")
    
    relevant_items.sort(key=lambda x: -x['weight'])
    return relevant_items[:MAX_RELEVANT_SNIPPETS]

def scrape_accessibility(driver, landmark, sources):
    accessibility_data = []
    
    for source in sources:
        try:
            logger.info(f"Analisando fonte: {source}")
            driver.get(source.split('#')[0])
            
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            body_text = driver.find_element(By.TAG_NAME, "body").text
            relevant_items = extract_relevant_content(body_text, source)
            
            if relevant_items:
                logger.info(f"Encontrados {len(relevant_items)} recursos de acessibilidade em {source}")
                accessibility_data.extend(relevant_items)
            else:
                logger.warning(f"Nenhum recurso de acessibilidade encontrado em {source}")
                
        except Exception as e:
            logger.error(f"Erro ao processar {source}: {str(e)[:200]}")
    
    return format_report(accessibility_data)

def format_report(accessibility_items):
    if not accessibility_items:
        return {
            "features": {},
            "score": 0,
            "found_any": False,
            "categories": {
                "mobilidade": 0,
                "visual": 0,
                "auditiva": 0,
                "geral": 0,
                "digital": 0,
                "cognitiva": 0
            }
        }
    
    features = {}
    total_score = 0
    category_scores = {
        "mobilidade": 0,
        "visual": 0,
        "auditiva": 0,
        "geral": 0,
        "digital": 0,
        "cognitiva": 0
    }
    
    for item in accessibility_items:
        feature = item['feature']
        if feature not in features:
            features[feature] = []
        features[feature].append(item)
        total_score += item['weight']
        category_scores[item['category']] += item['weight']
    
    return {
        "features": features,
        "score": total_score,
        "found_any": True,
        "categories": category_scores
    }

def classify_accessibility(report):
    if not report['found_any']:
        return ("Não Acessível", "red")
    
    score = report['score']
    MIN_ACESSIVEL = 10
    MIN_PARCIAL = 5
    
    if score >= MIN_ACESSIVEL:
        return ("Acessível", "green")
    elif score >= MIN_PARCIAL:
        return ("Parcialmente Acessível", "orange")
    else:
        return ("Não Acessível", "red")

def save_json(landmark, report, classification, sources):
    data = {
        "name": landmark,
        "report": report,
        "classification": classification[0],
        "color": classification[1],
        "sources": sources,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    os.makedirs("results", exist_ok=True)
    safe_landmark = re.sub(r'[\\/*?:"<>|]', '_', landmark)
    filename = f"results/{safe_landmark}_accessibility.json"

    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Arquivo JSON salvo: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Erro ao salvar JSON: {e}")
        return None

def get_coordinates(landmark):
    try:
        geolocator = Nominatim(user_agent="accessibility_map_brasilia_v13")
        
        query = f"{landmark}, Brasília, Distrito Federal, Brazil"
        location = geolocator.geocode(query, timeout=15)
        if location:
            logger.info(f"Coordenadas encontradas para {landmark} (Tentativa 1)")
            return [location.latitude, location.longitude]
        
        query = f"{landmark}, Brasília, Brazil"
        location = geolocator.geocode(query, timeout=15)
        if location:
            logger.info(f"Coordenadas encontradas para {landmark} (Tentativa 2)")
            return [location.latitude, location.longitude]
        
        query = landmark
        location = geolocator.geocode(query, timeout=15)
        if location:
            logger.info(f"Coordenadas encontradas para {landmark} (Tentativa 3)")
            return [location.latitude, location.longitude]
        
        logger.warning(f"Coordenadas não encontradas para {landmark}. Usando centro de Brasília.")
        return [-15.7942, -47.8825]
    
    except Exception as e:
        logger.error(f"Erro ao obter coordenadas para {landmark}: {e}")
        return [-15.7942, -47.8825]

def create_popup_html(name, classification, color, report):
    feature_names = {
        'rampas': 'Rampas de acesso',
        'elevadores': 'Elevadores acessíveis',
        'banheiros_adaptados': 'Banheiros adaptados',
        'plataformas_elevatorias': 'Plataformas elevatórias',
        'pisos_tateis': 'Pisos táteis',
        'braille': 'Sinalização em Braille',
        'painel_tatil': 'Painéis táteis',
        'recursos_auditivos': 'Recursos auditivos',
        'legendas': 'Legendas',
        'libras': 'Recursos em Libras',
        'vagas_especiais': 'Vagas especiais',
        'acesso_universal': 'Acesso universal',
        'acessibilidade_digital': 'Acessibilidade digital',
        'recursos_cognitivos': 'Recursos cognitivos',
        'assentos_acessiveis': 'Assentos acessíveis'
    }
    
    if not report['found_any']:
        accessibility_summary = "Nenhum recurso de acessibilidade identificado."
    else:
        features_list = [feature_names.get(feature, feature) for feature in report['features'].keys()]
        accessibility_summary = f"Recursos de acessibilidade: {', '.join(features_list)}."
    
    popup_html = f"""
    <div style="width: 420px; font-family: 'Arial', sans-serif; padding: 15px; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <div style="border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-bottom: 12px;">
            <h2 style="margin: 0; color: #2c3e50; font-size: 1.4em;">{html.escape(name)}</h2>
            <div style="background-color: {color}20; padding: 10px; border-radius: 5px; margin: 10px 0; 
                 font-weight: bold; color: {color}; border-left: 5px solid {color}; text-align: center; font-size: 1.1em;">
                Classificação: {classification} (Score: {report['score']})
            </div>
        </div>
        <div style="color: #34495e; font-size: 1em;">
            {accessibility_summary}
        </div>
    </div>
    """
    return popup_html

def plot_on_map(results):
    os.makedirs("results", exist_ok=True)
    
    map_center = [-15.7942, -47.8825]
    accessibility_map = folium.Map(location=map_center, zoom_start=13, tiles='cartodbpositron')
    
    font_awesome = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    """
    accessibility_map.get_root().header.add_child(folium.Element(font_awesome))
    
    for item in results:
        name = item['name']
        classification_tuple = item['classification']
        classification = classification_tuple[0]
        color = classification_tuple[1]
        report = item['report']
        
        coords = get_coordinates(name)
        if not coords:
            logger.warning(f"Ignorando {name} devido à falta de coordenadas.")
            continue
        
        popup_html = create_popup_html(name, classification, color, report)
        
        icon_choice = "wheelchair" if classification == "Acessível" else "exclamation-triangle" if classification == "Parcialmente Acessível" else "ban"
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=450),
            icon=folium.Icon(color=color, icon=icon_choice, prefix='fa'),
            tooltip=f"{name} - {classification}"
        ).add_to(accessibility_map)
    
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; 
                background: linear-gradient(to bottom, #ffffff, #f1f5f9); 
                border: 2px solid #3498db; z-index: 9999; font-size: 14px;
                padding: 15px; border-radius: 10px; font-family: 'Arial', sans-serif;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h4 style="margin: 0 0 10px 0; text-align: center; color: #2c3e50; 
                   font-size: 16px; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px;">
            Legenda
        </h4>
        <div style="margin: 8px 0; display: flex; align-items: center;">
            <i class="fa fa-wheelchair" style="color: green; font-size: 18px; margin-right: 8px;"></i>
            <span style="color: #2c3e50;">Acessível</span>
        </div>
        <div style="margin: 8px 0; display: flex; align-items: center;">
            <i class="fa fa-exclamation-triangle" style="color: orange; font-size: 18px; margin-right: 8px;"></i>
            <span style="color: #2c3e50;">Parcialmente Acessível</span>
        </div>
        <div style="margin: 8px 0; display: flex; align-items: center;">
            <i class="fa fa-ban" style="color: red; font-size: 18px; margin-right: 8px;"></i>
            <span style="color: #2c3e50;">Não Acessível</span>
        </div>
    </div>
    """
    accessibility_map.get_root().html.add_child(folium.Element(legend_html))
    
    map_path = os.path.join("results", "accessibility_map.html")
    accessibility_map.save(map_path)
    logger.info(f"Mapa gerado: {map_path}")

def main():
    logger.info("Iniciando análise de acessibilidade...")
    
    os.makedirs("results", exist_ok=True)
    driver = setup_driver()
    landmarks = read_tourist_file("tourist_attractions.txt")
    
    if not landmarks:
        logger.error("Nenhum ponto turístico encontrado no arquivo.")
        driver.quit()
        return
    
    results = []
    for landmark in landmarks:
        logger.info(f"Processando: {landmark['name']}")
        
        report = scrape_accessibility(driver, landmark['name'], landmark['sources'])
        classification = classify_accessibility(report)
        
        logger.info(f"Classificação: {classification[0]} (Score: {report['score']})")
        logger.info("Recursos encontrados:")
        for feature, items in report['features'].items():
            logger.info(f" - {feature}: {len(items)} itens (peso total: {sum(i['weight'] for i in items)})")
        
        logger.info("Pontuação por Categoria:")
        for category, score in report['categories'].items():
            logger.info(f" - {category.title()}: {score} pontos")
        
        json_file = save_json(landmark['name'], report, classification, landmark['sources'])
        results.append({
            'name': landmark['name'],
            'classification': classification,
            'report': report
        })
    
    driver.quit()
    logger.info("Gerando mapa interativo...")
    plot_on_map(results)
    logger.info("Análise concluída com sucesso!")

if __name__ == "__main__":
    main()
