import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from geopy.geocoders import Nominatim
import folium
import re
import html
from urllib.parse import urlparse
import os

# Configurações globais
TIMEOUT = 30
MAX_RELEVANT_SNIPPETS = 10

# Sistema Completo de Recursos de Acessibilidade
ACCESSIBILITY_FEATURES = {
    'rampas': {
        'terms': [
            r'rampa[s]? de acesso', r'acesso[s]? para cadeirante[s]?', r'acesso[s]? sem degrau[s]?',
            r'rampa[s]? inclinada[s]?', r'rampa[s]? de entrada', r'rampa[s]? de circulação',
            r'rampa[s]? de acessibilidade', r'rampa[s]? para cadeira de rodas',
            r'rampa[s]? de desnível', r'rampa[s]? de transposição', r'acesso[s]? para mobilidade reduzida',
            r'rampa[s]? portátil[is]?', r'acesso[s]? por rampa', r'rampa[s]? com corrimão',
            r'rampa[s]? com inclinação adequada', r'acesso[s]? para pessoas com mobilidade'
        ],
        'weight': 2,
        'category': 'mobilidade',
        'regex': True
    },
    'elevadores': {
        'terms': [
            r'elevador[es]? acess[íi]ve[is]?', r'elevador[es]? para cadeirante[s]?',
            r'elevador[es]? adaptado[s]?', r'elevador[es]? inclusivo[s]?',
            r'elevador[es]? para deficiente[s]?', r'elevador[es]? com bot[ôo]es em braille',
            r'elevador[es]? com sinaliza[çc][ãa]o t[áa]til', r'elevador[es]? com voz',
            r'elevador[es]? interno[s]?', r'elevador[es]? para PCD',
            r'elevador[es]? com porta larga', r'elevador[es]? com espaço para cadeiras',
            r'elevador[es]? de acessibilidade', r'elevador[es]? com áudio', r'elevador[es]? com espelho',
            r'elevador[es]? para mobilidade reduzida', r'elevador[es]? com controles acessíveis'
        ],
        'weight': 3,
        'category': 'mobilidade',
        'regex': True
    },
    'banheiros_adaptados': {
        'terms': [
            r'banheiro[s]? adaptado[s]?', r'banheiro[s]? acess[íi]ve[is]?',
            r'sanit[áa]rio[s]? acess[íi]ve[is]?', r'vaso[s]? sanit[áa]rio[s]? adaptado[s]?',
            r'banheiro[s]? para deficiente[s]?', r'banheiro[s]? inclusivo[s]?',
            r'banheiro[s]? para cadeirante[s]?', r'banheiro[s]? com barras de apoio',
            r'banheiro[s]? com pia adaptada', r'banheiro[s]? com porta larga',
            r'banheiro[s]? com espa[çc]o para cadeira de rodas', r'banheiro[s]? PCD',
            r'toalete[s]? adaptado[s]?', r'banheiro[s]? para pessoas com deficiência',
            r'banheiro[s]? com assento elevado', r'banheiro[s]? com espaço de manobra',
            r'banheiro[s]? com sinalização acessível', r'banheiro[s]? com acessórios adaptados'
        ],
        'weight': 3,
        'category': 'mobilidade',
        'regex': True
    },
    'plataformas_elevatorias': {
        'terms': [
            r'plataforma[s]? elevat[óo]ria[s]?', r'elevador[es]? vertical[is]?',
            r'plataforma[s]? de acesso', r'plataforma[s]? para cadeirante[s]?',
            r'elevador[es]? de plataforma', r'plataforma[s]? inclusiva[s]?',
            r'plataforma[s]? de mobilidade', r'plataforma[s]? acess[íi]vel[is]?',
            r'plataforma[s]? para deficiente[s]?', r'plataforma[s]? de transposição',
            r'plataforma[s]? com controles acessíveis', r'plataforma[s]? de elevação',
            r'dispositivo[s]? de elevação', r'plataforma[s]? para mobilidade reduzida',
            r'plataforma[s]? com segurança', r'elevador[es]? de acesso'
        ],
        'weight': 3,
        'category': 'mobilidade',
        'regex': True
    },
    'pisos_tateis': {
        'terms': [
            r'piso[s]? t[áa]te[is]?', r'piso[s]? podot[áa]te[is]?',
            r'sinaliza[çc][ãa]o t[áa]til no piso', r'piso[s]? para deficiente[s]? visua[is]?',
            r'piso[s]? direcional[is]?', r'sinaliza[çc][ãa]o t[áa]til',
            r'piso[s]? de alerta', r'piso[s]? guia', r'piso[s]? de orienta[çc][ãa]o',
            r'piso[s]? com textura', r'piso[s]? para cegos', r'piso[s]? de seguran[çc]a',
            r'piso[s]? com contraste', r'guia[s]? t[áa]til[is]?', r'piso[s]? de acessibilidade',
            r'caminho[s]? t[áa]til[is]?', r'piso[s]? com relevo', r'orienta[çc][ãa]o t[áa]til no ch[ãa]o'
        ],
        'weight': 2,
        'category': 'visual',
        'regex': True
    },
    'braille': {
        'terms': [
            r'braille', r'braile', r'sinaliza[çc][ãa]o em braille',
            r'placa[s]? em braille', r'informa[çc][õo]es em braille',
            r'mapa[s]? t[áa]til[is]?', r'orienta[çc][õo]es em braille',
            r'bot[ôo]es em braille', r'descri[çc][ãa]o em braille',
            r'texto em braille', r'legenda em braille', r'menu em braille',
            r'identifica[çc][ãa]o em braille', r'rotulagem em braille',
            r'etiqueta[s]? em braille', r'painel em braille', r'sinal em braille',
            r'guia em braille', r'placa[s]? t[áa]til[is]? com braille', r'marca[çc][õo]es em braille'
        ],
        'weight': 2,
        'category': 'visual',
        'regex': True
    },
    'painel_tatil': {
        'terms': [
            r'pain[eé]is? t[áa]te[is]?', r'pain[eé]is? podot[áa]te[is]?',
            r'pain[eé]is? para deficiente[s]? visua[is]?', r'pain[eé]is? de orienta[çc][ãa]o t[áa]til',
            r'pain[eé]is? com informa[çc][õo]es t[áa]te[is]?', r'mapa[s]? t[áa]til[is]?',
            r'display t[áa]til', r'interface t[áa]til', r'terminal t[áa]til',
            r'painel de navega[çc][ãa]o t[áa]til', r'sistema de orienta[çc][ãa]o t[áa]til',
            r'guia t[áa]til', r'placa[s]? t[áa]til[is]?', r'dispositivo[s]? t[áa]til[is]?',
            r'painel com relevo', r'orienta[çc][ãa]o para cegos', r'mapa[s]? de acessibilidade'
        ],
        'weight': 2,
        'category': 'visual',
        'regex': True
    },
    'recursos_auditivos': {
        'terms': [
            r'sinaliza[çc][ãa]o sonora', r'audioguia[s]?', r'audiodescri[çc][ãa]o',
            r'sistema[s]? de [áa]udio', r'informa[çc][ãa]o em [áa]udio',
            r'guias de [áa]udio', r'tour de [áa]udio', r'orienta[çc][ãa]o por [áa]udio',
            r'narra[çc][ãa]o sonora', r'descri[çc][ãa]o por [áa]udio',
            r'sistema de som adaptado', r'[áa]udio descritivo',
            r'fone[s]? de indu[çc][ãa]o magn[ée]tica', r'sistema FM',
            r'loop auditivo', r'amplificador de som', r'dispositivo[s]? de [áa]udio',
            r'[áa]udio para deficiente[s]? visua[is]?', r'sinal sonoro', r'alertas sonoros',
            r'sistema de [áa]udio acess[íi]vel', r'narra[çc][ãa]o em tempo real'
        ],
        'weight': 2,
        'category': 'auditiva',
        'regex': True
    },
    'legendas': {
        'terms': [
            r'legenda[s]?', r'legenda[s]? inclusiva[s]?', r'legenda[s]? para surdo[s]?',
            r'legenda[s]? descritiva[s]?', r'legenda[s]? em v[íi]deo[s]?',
            r'legenda[s]? em tempo real', r'closed caption', r'cc[ ]?[0-9]?',
            r'subt[íi]tulo[s]? para deficiente[s]? auditivo[s]?', r'legenda[s]? acess[íi]ve[is]?',
            r'sistema de legenda', r'legenda[s]? em libras',
            r'legenda[s]? para deficiente[s]? auditivo[s]?', r'legenda[s]? simult[âa]nea[s]?',
            r'subt[íi]tulo[s]? acess[íi]vel[is]?', r'legenda[s]? ao vivo', r'texto descritivo',
            r'subt[íi]tulo[s]? em tempo real', r'legenda[s]? para PCD', r'sistema de subtitula[çc][ãa]o'
        ],
        'weight': 2,
        'category': 'auditiva',
        'regex': True
    },
    'libras': {
        'terms': [
            r'int[ée]rprete[s]? de libras', r'v[íi]deo[s]? em libras', r'atendimento em libras',
            r'l[íi]ngua brasileira de sinais', r'tradu[çc][ãa]o para libras',
            r'sinaliza[çc][ãa]o em libras', r'guias em libras', r'orienta[çc][ãa]o em libras',
            r'linguagem de sinais', r'comunica[çc][ãa]o por sinais',
            r'tradu[çc][ãa]o simult[âa]nea em libras', r'janela de libras',
            r'int[ée]rprete de sinais', r'libras no local',
            r'L[íi]ngua de Sinais Brasileira', r'interpreta[çc][ãa]o em LIBRAS',
            r'atendimento para surdo[s]?', r'comunica[çc][ãa]o em libras', r'v[íi]deo[s]? acess[íi]ve[is]? em libras',
            r'servi[çc]o de libras', r'interprete de l[íi]ngua de sinais'
        ],
        'weight': 3,
        'category': 'auditiva',
        'regex': True
    },
    'vagas_especiais': {
        'terms': [
            r'vaga[s]? especial[is]?', r'vaga[s]? para deficiente[s]?',
            r'estacionamento acess[íi]vel', r'vaga[s]? priorit[áa]ria[s]?',
            r'vaga[s]? para idoso[s]?', r'vaga[s]? para pessoa[s]? com defici[êe]ncia',
            r'vaga[s]? exclusiva[s]?', r'vaga[s]? reservada[s]?',
            r'vaga[s]? azul', r'vaga[s]? com sinaliza[çc][ãa]o especial',
            r'vaga[s]? ampliada[s]?', r'vaga[s]? para mobilidade reduzida',
            r'estacionamento para PCD', r'vaga[s]? com acesso f[áa]cil',
            r'vaga[s]? sinalizada[s]?', r'[áa]rea reservada para deficiente[s]?',
            r'vaga[s]? de acessibilidade', r'estacionamento priorit[áa]rio'
        ],
        'weight': 1,
        'category': 'geral',
        'regex': True
    },
    'acesso_universal': {
        'terms': [
            r'acesso universal', r'acessibilidade total', r'desenho universal',
            r'acessibilidade inclusiva', r'acessibilidade para todo[s]?',
            r'projeto universal', r'concep[çc][ãa]o universal',
            r'espa[çc]o universal', r'ambiente inclusivo',
            r'infraestrutura acess[íi]vel', r'local adaptado',
            r'espa[çc]o para todo[s]?', r'acesso sem barreira[s]?',
            r'arquitetura inclusiva', r'design inclusivo',
            r'ambiente acess[íi]vel', r'acesso para PCD', r'espa[çc]o sem obst[áa]culo[s]?',
            r'adapta[çc][ãa]o universal', r'acessibilidade ampla', r'design para todo[s]?'
        ],
        'weight': 3,
        'category': 'geral',
        'regex': True
    }
}

def setup_driver():
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(TIMEOUT)
    return driver

def read_tourist_file(file_path):
    landmarks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if '|' in line:
                    parts = [p.strip() for p in line.strip().split('|') if p.strip()]
                    if len(parts) > 1:
                        landmarks.append({
                            'name': parts[0],
                            'sources': parts[1:]
                        })
        return landmarks
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []

def extract_relevant_content(text, source):
    relevant_items = []
    text = text.lower()
    
    for feature, data in ACCESSIBILITY_FEATURES.items():
        for term_pattern in data['terms']:
            try:
                pattern = re.compile(term_pattern, re.IGNORECASE)
                matches = pattern.finditer(text)
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    snippet = html.unescape(text[start:end].strip())
                    snippet = ' '.join(snippet.split())
                    
                    term_exists = any(item['term'].lower() == match.group().lower() and 
                                      item['feature'] == feature for item in relevant_items)
                    
                    if not term_exists:
                        relevant_items.append({
                            'feature': feature,
                            'term': match.group(),
                            'snippet': snippet,
                            'weight': data['weight'],
                            'category': data['category'],
                            'source': source
                        })
            except Exception as e:
                print(f"Erro ao processar padrão '{term_pattern}': {e}")
                continue
    
    relevant_items.sort(key=lambda x: -x['weight'])
    return relevant_items[:MAX_RELEVANT_SNIPPETS]

def scrape_accessibility(driver, landmark, sources):
    accessibility_data = []
    
    for source in sources:
        try:
            print(f"\n🔍 Analisando: {source}")
            driver.get(source.split('#')[0])
            
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
            
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            body_text = driver.find_element(By.TAG_NAME, "body").text
            relevant_items = extract_relevant_content(body_text, source)
            
            if relevant_items:
                print(f"   ✅ Encontrados {len(relevant_items)} recursos de acessibilidade")
                for item in relevant_items:
                    print(f"     - {item['feature']}: '{item['term']}' (peso: {item['weight']})")
                accessibility_data.extend(relevant_items)
            else:
                print("   ⚠️ Nenhum recurso de acessibilidade encontrado")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar: {str(e)[:200]}...")
    
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
                "geral": 0
            }
        }
    
    features = {}
    total_score = 0
    category_scores = {
        "mobilidade": 0,
        "visual": 0,
        "auditiva": 0,
        "geral": 0
    }
    
    for item in accessibility_items:
        if item['feature'] not in features:
            features[item['feature']] = []
        features[item['feature']].append(item)
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
    filename = f"results/{re.sub(r'[\\/*?:\"<>|]', '_', landmark)}_accessibility.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"   💾 Arquivo salvo: {filename}")
        return filename
    except Exception as e:
        print(f"   ❌ Erro ao salvar JSON: {e}")
        return None

def get_coordinates(landmark):
    try:
        geolocator = Nominatim(user_agent="accessibility_map_brasilia_v12")
        
        query = f"{landmark}, Brasília, Distrito Federal, Brazil"
        location = geolocator.geocode(query, timeout=15)
        if location:
            print(f"   📍 Coordenadas encontradas para {landmark} (Tentativa 1)")
            return [location.latitude, location.longitude]
        
        query = f"{landmark}, Brasília, Brazil"
        location = geolocator.geocode(query, timeout=15)
        if location:
            print(f"   📍 Coordenadas encontradas para {landmark} (Tentativa 2)")
            return [location.latitude, location.longitude]
        
        query = landmark
        location = geolocator.geocode(query, timeout=15)
        if location:
            print(f"   📍 Coordenadas encontradas para {landmark} (Tentativa 3)")
            return [location.latitude, location.longitude]
        
        print(f"   ⚠️ Coordenadas não encontradas para {landmark}. Usando centro de Brasília como fallback.")
        return [-15.7942, -47.8825]
    
    except Exception as e:
        print(f"   ❌ Erro ao obter coordenadas para {landmark}: {e}. Usando centro de Brasília como fallback.")
        return [-15.7942, -47.8825]

def create_popup_html(name, classification, color, report):
    feature_names = {
        'rampas': 'Rampas de Acesso',
        'elevadores': 'Elevadores Acessíveis',
        'banheiros_adaptados': 'Banheiros Adaptados',
        'plataformas_elevatorias': 'Plataformas Elevatórias',
        'pisos_tateis': 'Pisos Táteis',
        'braille': 'Sinalização em Braille',
        'painel_tatil': 'Painéis Táteis',
        'recursos_auditivos': 'Recursos Auditivos',
        'legendas': 'Legendas e Legendagem',
        'libras': 'Recursos em Libras',
        'vagas_especiais': 'Vagas Especiais',
        'acesso_universal': 'Acesso Universal'
    }
    
    features_html = ""
    for feature, items in report['features'].items():
        items_html = ""
        for item in items[:3]:
            source_domain = urlparse(item.get('source', '')).netloc if item.get('source') else 'Fonte não disponível'
            items_html += f"""
            <div style="margin-bottom: 8px;">
                <div style="font-weight: bold; color: #2c3e50;">• {item['term'].title()}:</div>
                <div style="font-size: 0.9em; margin-left: 10px; color: #34495e;">{html.escape(item['snippet'])}</div>
                <div style="font-size: 0.8em; color: #7f8c8d; margin-top: 2px;">Fonte: {source_domain}</div>
            </div>
            """
        
        features_html += f"""
        <div style="margin-bottom: 12px; border-bottom: 1px solid #ecf0f1; padding-bottom: 8px;">
            <h4 style="margin: 0 0 5px 0; color: #2980b9;">{feature_names.get(feature, feature)}</h4>
            {items_html}
        </div>
        """
    
    categories_html = ""
    if report['found_any']:
        categories_html = """
        <div style="margin-top: 10px; padding: 8px; background-color: #ecf0f1; border-radius: 5px;">
            <h4 style="margin: 0 0 5px 0; color: #2980b9;">Resumo por Categoria</h4>
            <div style="display: flex; justify-content: space-between;">
        """
        
        for category, score in report['categories'].items():
            categories_html += f"""
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #2c3e50;">{category.title()}</div>
                    <div style="color: #34495e;">{score} pts</div>
                </div>
            """
        
        categories_html += """
            </div>
        </div>
        """
    
    popup_html = f"""
    <div style="width: 420px; max-height: 500px; overflow-y: auto; font-family: 'Arial', sans-serif; padding: 15px; background: #fff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <div style="border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; margin-bottom: 12px;">
            <h2 style="margin: 0; color: #2c3e50; font-size: 1.4em;">{html.escape(name)}</h2>
            <div style="background-color: {color}20; padding: 10px; border-radius: 5px; margin: 10px 0; 
                 font-weight: bold; color: {color}; border-left: 5px solid {color}; text-align: center; font-size: 1.1em;">
                Classificação: {classification} (Score: {report['score']})
            </div>
        </div>
        <div style="max-height: 350px; overflow-y: auto; padding-right: 5px;">
            {features_html}
        </div>
        {categories_html}
    </div>
    """
    return popup_html

def plot_on_map(results):
    os.makedirs("results", exist_ok=True)
    
    map_center = [-15.7942, -47.8825]
    accessibility_map = folium.Map(location=map_center, zoom_start=13, tiles='cartodbpositron')
    
    # Adiciona o CDN do FontAwesome para garantir que os ícones sejam exibidos
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
            print(f"   ⚠️ Ignorando {name} devido à falta de coordenadas.")
            continue
        
        popup_html = create_popup_html(name, classification, color, report)
        
        # Escolhe o ícone baseado na classificação
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
    print(f"\n🗺️ Mapa gerado com sucesso em: {map_path}")

def main():
    print("🚀 Iniciando análise de acessibilidade...\n")
    
    os.makedirs("results", exist_ok=True)
    driver = setup_driver()
    landmarks = read_tourist_file("tourist_attractions.txt")
    
    if not landmarks:
        print("Nenhum ponto turístico encontrado no arquivo.")
        driver.quit()
        return
    
    results = []
    for landmark in landmarks:
        print(f"\n{'='*70}\n🔷 Processando: {landmark['name']}")
        
        report = scrape_accessibility(driver, landmark['name'], landmark['sources'])
        classification = classify_accessibility(report)
        
        print(f"\n📋 Classificação: {classification[0]}")
        print(f"📊 Score Total: {report['score']}")
        print(f"📌 Recursos encontrados:")
        for feature, items in report['features'].items():
            print(f" - {feature}: {len(items)} itens (peso total: {sum(i['weight'] for i in items)})")
        
        print(f"\n📊 Pontuação por Categoria:")
        for category, score in report['categories'].items():
            print(f" - {category.title()}: {score} pontos")
        
        json_file = save_json(landmark['name'], report, classification, landmark['sources'])
        results.append({
            'name': landmark['name'],
            'classification': classification,
            'report': report
        })
    
    driver.quit()
    print("\n📊 Gerando mapa interativo...")
    plot_on_map(results)
    print("\n✅ Análise concluída com sucesso!")

if __name__ == "__main__":
    main()
