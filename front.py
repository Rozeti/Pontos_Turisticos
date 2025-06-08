import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy_garden.mapview import MapView, MapMarkerPopup, MarkerMapLayer
import os
import json

# Definindo as cores para consistência com o protótipo (tema escuro)
PRIMARY_COLOR = get_color_from_hex('#1A1A1A') # Cor de fundo principal
SECONDARY_COLOR = get_color_from_hex('#2E2E2E') # Cor dos painéis/inputs
TEXT_COLOR = get_color_from_hex('#FFFFFF') # Cor do texto branco
ACCENT_COLOR_GREEN = get_color_from_hex('#4CAF50') # Verde para "aprovado" / alto
ACCENT_COLOR_YELLOW = get_color_from_hex('#FFEB3B') # Amarelo para "parcial" / médio
ACCENT_COLOR_RED = get_color_from_hex('#F44336') # Vermelho para "não aprovado" / baixo

# O Kivy Language (KV) para definir o layout das telas
# Isso permite separar a definição do layout da lógica Python.
KV_CODE = """
<MainScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgb: app.primary_color
            Rectangle:
                pos: self.pos
                size: self.size

        # Logo TurSeguro
        Image:
            source: 'logo_turseguro.png' # Você precisará ter esta imagem no diretório
            size_hint: (0.3, 0.2)
            pos_hint: {'center_x': 0.5, 'top': 0.9}
            allow_stretch: True
            keep_ratio: True

        Label:
            text: 'Descubra destinos turísticos acessíveis e seguros'
            color: app.text_color
            size_hint_y: None
            height: dp(40)
            pos_hint: {'center_x': 0.5, 'top': 0.7}
            font_size: '20sp'

        BoxLayout:
            orientation: 'horizontal'
            size_hint: (0.8, 0.1)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            padding: dp(10)
            spacing: dp(10)

            TextInput:
                id: search_input
                hint_text: 'Pesquisar'
                multiline: False
                background_color: app.secondary_color
                foreground_color: app.text_color
                hint_text_color: app.text_color
                font_size: '18sp'
                padding: [dp(15), (self.height - self.line_height) / 2]
                size_hint_x: 0.9
                on_text_validate: root.search_location(self.text) # Ao pressionar Enter

            Button:
                background_normal: ''
                background_color: app.secondary_color
                size_hint_x: 0.1
                on_release: root.search_location(search_input.text)
                Image:
                    source: 'search_icon.png' # Ícone de lupa, precisa ser fornecido
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    size: dp(30), dp(30)
                    color: app.text_color

        MapView:
            id: mapview
            size_hint: (1, 0.6)
            pos_hint: {'x': 0, 'y': 0}
            zoom: 12
            lat: -15.793889  # Centro Brasília (ajuste se quiser)
            lon: -47.882778


<DetailScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgb: app.primary_color
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            orientation: 'horizontal'
            size_hint: (1, 1)

            # Painel esquerdo de detalhes
            ScrollView:
                size_hint: (0.4, 1) # Ocupa 40% da largura
                canvas.before:
                    Color:
                        rgb: app.secondary_color
                    Rectangle:
                        pos: self.pos
                        size: self.size

                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(20)
                    spacing: dp(15)

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        padding: [0, dp(10), 0, dp(10)]
                        
                        Button:
                            text: '< Voltar'
                            size_hint_x: None
                            width: dp(100)
                            background_normal: ''
                            background_color: app.primary_color
                            on_release: app.root.current = 'main_screen'
                        
                        Image:
                            source: 'logo_turseguro.png'
                            size_hint_x: None
                            width: dp(50)
                            allow_stretch: True
                            keep_ratio: True
                            
                        Label:
                            text: 'TurSeguro'
                            color: app.text_color
                            font_size: '22sp'
                            bold: True
                            size_hint_x: 1
                            text_size: self.size
                            valign: 'middle'

                    TextInput:
                        id: detail_search_input
                        hint_text: 'Pesquisar...'
                        multiline: False
                        background_color: app.primary_color
                        foreground_color: app.text_color
                        hint_text_color: app.text_color
                        font_size: '18sp'
                        padding: [dp(15), (self.height - self.line_height) / 2]
                        size_hint_y: None
                        height: dp(60)
                        on_text_validate: root.search_location(self.text)

                    # Seção de Acessibilidade
                    Label:
                        text: 'Acessibilidade'
                        color: app.text_color
                        font_size: '20sp'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                        text_size: self.size
                        valign: 'middle'

                    GridLayout:
                        id: accessibility_grid 
                        cols: 2
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(10)
                        row_default_height: dp(30)
                        row_force_default: True
                        Label:
                            text: 'Mobilidade'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: mobilidade_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Visual'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: visual_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Auditiva'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: auditiva_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Geral'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: geral_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Digital'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: digital_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Cognitiva'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: cognitiva_value
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'

                    # Relatório Descritivo
                    Label:
                        text: 'Relatório descritivo'
                        color: app.text_color
                        font_size: '20sp'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                        text_size: self.size
                        valign: 'middle'
                    Label:
                        id: report_label
                        text: ""
                        color: app.text_color
                        font_size: '16sp'
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.width, None
                        valign: 'top'

            # Área do mapa (direita)
            FloatLayout:
                size_hint: (0.6, 1)
                canvas.before:
                    Color:
                        rgb: app.primary_color
                    Rectangle:
                        pos: self.pos
                        size: self.size
                MapView:
                    id: mapview_details
                    size_hint: (1, 0.6)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.4}
                    zoom: 12
                    lat: -15.793889  # Centro Brasília (ajuste se quiser)
                    lon: -47.882778
                BoxLayout:
                    id: map_popup
                    orientation: 'vertical'
                    size_hint: (1, 0.2)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.9}
                    padding: dp(10)
                    spacing: dp(5)
                    canvas.before:
                        Color:
                            rgb: app.secondary_color
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    Label:
                        id: popup_title
                        text: 'Pop-up do Mapa'
                        color: app.text_color
                        font_size: '16sp'
                        bold: True
                        text_size: self.width, None
                        halign: 'left'
                    Label:
                        id: popup_status
                        text: ''
                        color: app.text_color
                        font_size: '14sp'
                        text_size: self.width, None
                        halign: 'left'
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(10)
                        Image:
                            source: 'star_icon.png'
                            size_hint_x: None
                            width: dp(30)
                            allow_stretch: True
                            keep_ratio: True
                            color: app.text_color
                        Label:
                            id: popup_rating
                            text: ''
                            color: app.text_color
                            font_size: '18sp'
                            halign: 'left'
                            text_size: self.width, None
"""

# Carregar o KV_CODE
Builder.load_string(KV_CODE)

class MainScreen(Screen):
    """
    Tela principal para buscar locais e visualizar o mapa.
    """
    def search_location(self, text):
        """
        Método chamado ao pesquisar um local.
        Busca na lista carregada do .txt.
        """
        print(f"Pesquisando por: {text}")
        
        app = App.get_running_app()
        search_text = text.lower().strip()
        
        found_name = None
        for location_name in app.locations_data:
            if search_text in location_name.lower():
                found_name = location_name
                break
        
        if found_name:
            detail_screen = self.manager.get_screen('detail_screen')
            # CHAMADA ATUALIZADA para o método renomeado
            detail_screen.load_details(location_name=found_name)
            self.manager.current = 'detail_screen'
        else:
            print(f"Local '{text}' não encontrado.")
            self.ids.search_input.text = f"'{text}' não encontrado!"
        
    def on_pre_enter(self):
        """Adicionar marcadores toda vez que a tela for mostrada."""
        mapview = self.ids.mapview
        app = App.get_running_app()
        mapview.map_source = "osm"

        for point in app.points_data:
            lat = point['coordinates']['latitude']
            lon = point['coordinates']['longitude']
            color = point.get('color', 'red')

            # Criar um marcador com popup
            marker = MapMarkerPopup(lat=lat, lon=lon)   

            # Personalizar o popup do marcador
            popup = Label(
                text=f"{point['name']}\nClassificação: {point['classification']}",
                size_hint=(None, None),
                size=(200, 100),
                color=(1, 1, 1, 1),
                text_size=(180, None)
            )
            marker.add_widget(popup)

            # Salvar os dados para usar depois (ex: para abrir detalhes)
            marker.point_data = point

            # Bind para clicar e mostrar detalhes
            marker.bind(on_release=self.marker_clicked)

            mapview.add_widget(marker)

    def marker_clicked(self, marker):
        app = App.get_running_app()
        detail_screen = self.manager.get_screen('detail_screen')
        detail_screen.load_details(marker.point_data['name'])
        self.manager.current = 'detail_screen'

class DetailScreen(Screen):
    """
    Tela para exibir detalhes de um ponto turístico.
    """
    current_marker = False

    # MÉTODO RENOMEADO E MODIFICADO
    def load_details(self, location_name):
        app = App.get_running_app()
        point = next((p for p in app.points_data if p['name'] == location_name), None)

        if not point:
            self.ids.report_label.text = f"Dados para '{location_name}' não encontrados."
            return

        mobilidade_value = point.get('report', 'N/D').get('categories', 'N/D').get('mobilidade', 'N/D')
        visual_value = point.get('report', 'N/D').get('categories', 'N/D').get('visual', 'N/D')
        auditiva_value = point.get('report', 'N/D').get('categories', 'N/D').get('auditiva', 'N/D')
        geral_value = point.get('report', 'N/D').get('categories', 'N/D').get('geral', 'N/D')
        digital_value = point.get('report', 'N/D').get('categories', 'N/D').get('digital', 'N/D')
        cognitiva_value = point.get('report', 'N/D').get('categories', 'N/D').get('cognitiva', 'N/D')

        self.ids.detail_search_input.text = location_name
        self.ids.mobilidade_value.text = str(mobilidade_value)
        self.ids.visual_value.text = str(visual_value)
        self.ids.auditiva_value.text = str(auditiva_value)
        self.ids.geral_value.text = str(geral_value)
        self.ids.digital_value.text = str(digital_value)
        self.ids.cognitiva_value.text = str(cognitiva_value)

        mapview = self.ids.mapview_details
        lat = point.get('coordinates', 'N/D').get('latitude', 'N/D')
        lon = point.get('coordinates', 'N/D').get('longitude', 'N/D')
        marker = MapMarkerPopup(lat=lat, lon=lon)   
        marker.point_data = point
        if self.current_marker != False:
            mapview.remove_widget(self.current_marker)
        self.current_marker = marker
        mapview.add_widget(marker)

        # Exemplo para atualizar a classificação e cores (você pode expandir)
        classification = point.get('classification', 'N/D')
        color_map = {'red': (1, 0, 0, 1), 'yellow': (1, 1, 0, 1), 'green': (0, 1, 0, 1)}
        color = color_map.get(point.get('color', 'red'), (1, 1, 1, 1))

        self.ids.report_label.text = f"Classificação: {classification}"

        # Atualize os labels de acessibilidade, segurança etc. aqui com os dados do point['report']['categories'] ou outros campos
        # Por simplicidade, deixo você implementar essa parte detalhada

        self.ids.popup_title.text = location_name
        self.ids.popup_status.text = classification
        self.ids.popup_rating.text = str(point.get('report', {}).get('score', 'N/D'))


    def search_location(self, text):
        """Método chamado ao pesquisar um local na tela de detalhes."""
        print(f"Pesquisando (na tela de detalhes) por: {text}")
        main_screen = self.manager.get_screen('main_screen')
        main_screen.ids.search_input.text = text 
        self.manager.current = 'main_screen'


class TurismoAcessivelApp(App):
    """
    Classe principal do aplicativo Kivy.
    """
    locations_data = []

    primary_color = PRIMARY_COLOR
    secondary_color = SECONDARY_COLOR
    text_color = TEXT_COLOR
    accent_color_green = ACCENT_COLOR_GREEN
    accent_color_yellow = ACCENT_COLOR_YELLOW
    accent_color_red = ACCENT_COLOR_RED

    points_data = []

    def build(self):
        self.title = 'Turismo Acessível DF'
        self.load_data_from_json()
        self.load_data_from_txt()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(DetailScreen(name='detail_screen'))
        return sm
    
    def load_data_from_txt(self):
        """Lê os nomes dos locais do arquivo .txt e os armazena na lista."""
        file_path = 'tourist_attractions.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.locations_data.append(line.split('|')[0])
            print(f"Dados carregados de {file_path}: {len(self.locations_data)} locais encontrados.")
        except FileNotFoundError:
            print(f"AVISO: O arquivo '{file_path}' não foi encontrado. A busca não funcionará.")

    def load_data_from_json(self):
        folder = 'results'
        self.points_data = []
        if not os.path.exists(folder):
            print(f"Pasta {folder} não encontrada.")
            return
        
        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                filepath = os.path.join(folder, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.points_data.append(data)
                        self.locations_data.append(data)
                except Exception as e:
                    print(f"Erro ao ler {filename}: {e}")
        print(f"{len(self.points_data)} pontos carregados da pasta {folder}.")


if __name__ == '__main__':
    # Para o aplicativo funcionar, você deve fornecer os seguintes arquivos de imagem
    # no mesmo diretório que o seu script Python:
    # 1. logo_turseguro.png
    # 2. search_icon.png
    # 3. star_icon.png
    
    TurismoAcessivelApp().run()
