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
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.properties import ListProperty
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIMARY_COLOR = get_color_from_hex("#0E0E0E")
SECONDARY_COLOR = get_color_from_hex('#0E0E0E')
TEXT_COLOR = get_color_from_hex('#FFFFFF')
ACCENT_COLOR_GREEN = get_color_from_hex('#4CAF50')
ACCENT_COLOR_YELLOW = get_color_from_hex('#FFEB3B')
ACCENT_COLOR_RED = get_color_from_hex('#F44336')

KV_CODE = """
<MainScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgb: app.primary_color
            Rectangle:
                pos: self.pos
                size: self.size

        Image:
            source: 'logo_turseguro.png'
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
                on_text_validate: root.search_location(self.text)

            Button:
                background_normal: ''
                background_color: app.secondary_color
                size_hint_x: 0.1
                on_release: root.search_location(search_input.text)
                Image:
                    source: 'search_icon.png'
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    size: dp(30), dp(30)
                    color: app.text_color

        MapView:
            id: mapview
            size_hint: (1, 0.6)
            pos_hint: {'x': 0, 'y': 0}
            zoom: 12
            lat: -15.793889
            lon: -47.882778

<DetailScreen>:
    square_color: [1, 1, 1, 1]
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

            ScrollView:
                size_hint: (0.4, 1)
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
                            size_hint_x: 2
                            width: dp(50)
                            allow_stretch: True
                            keep_ratio: True

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
                    lat: -15.793889
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
                        height: dp(30)
                        spacing: dp(10)
                        Widget:
                            size_hint_x: None
                            width: dp(30)
                            canvas:
                                Color:
                                    rgba: root.square_color
                                Rectangle:
                                    pos: self.pos
                                    size: dp(30), dp(30)
                        Label:
                            id: popup_rating
                            text: ''
                            color: app.text_color
                            font_size: '18sp'
                            halign: 'left'
                            text_size: self.width, None
"""

Builder.load_string(KV_CODE)

class MainScreen(Screen):
    def search_location(self, text):
        logger.info(f"Pesquisando por: {text}")
        app = App.get_running_app()
        search_text = text.lower().strip()
        
        found_name = None
        for location_name in app.locations_data:
            if search_text in location_name.lower():
                found_name = location_name
                break
        
        if found_name:
            detail_screen = self.manager.get_screen('detail_screen')
            detail_screen.load_details(location_name=found_name)
            self.manager.current = 'detail_screen'
        else:
            logger.warning(f"Local '{text}' não encontrado.")
            self.ids.search_input.text = f"'{text}' não encontrado!"
    
    def on_pre_enter(self):
        mapview = self.ids.mapview
        app = App.get_running_app()
        mapview.map_source = "osm"

        for widget in mapview.children[:]:
            if isinstance(widget, MapMarkerPopup):
                mapview.remove_widget(widget)

        marker_images = {
            'green': 'marker_green.png',
            'red': 'marker_red.png',
            'yellow': 'marker_yellow.png'
        }

        for point in app.points_data:
            lat = point.get('coordinates', {}).get('latitude')
            lon = point.get('coordinates', {}).get('longitude')
            if lat is None or lon is None:
                logger.warning(f"Coordenadas inválidas para {point.get('name', 'desconhecido')}")
                continue

            color = point.get('color', 'red')
            marker_image = marker_images.get(color, 'marker_red.png')
            
            if not os.path.exists(marker_image):
                logger.warning(f"Imagem do marcador '{marker_image}' não encontrada. Usando marcador padrão.")
                marker = MapMarkerPopup(lat=lat, lon=lon)
            else:
                marker = MapMarkerPopup(lat=lat, lon=lon, source=marker_image)

            popup = Label(
                text=f"{point['name']}\\nClassificação: {point['classification']}",
                size_hint=(None, None),
                size=(200, 100),
                color=(1, 1, 1, 1),
                text_size=(180, None)
            )
            marker.add_widget(popup)

            marker.point_data = point

            marker.bind(on_release=self.marker_clicked)

            mapview.add_widget(marker)
            logger.info(f"Marcador adicionado: {point['name']} ({lat}, {lon}) com cor {color}")

    def marker_clicked(self, marker):
        app = App.get_running_app()
        detail_screen = self.manager.get_screen('detail_screen')
        detail_screen.load_details(marker.point_data['name'])
        self.manager.current = 'detail_screen'

class DetailScreen(Screen):
    square_color = ListProperty([1, 1, 1, 1])
    current_marker = False

    def load_details(self, location_name):
        app = App.get_running_app()
        point = next((p for p in app.points_data if p['name'] == location_name), None)

        if not point:
            self.ids.report_label.text = f"Dados para '{location_name}' não encontrados."
            logger.warning(f"Dados não encontrados para '{location_name}'")
            return

        mobilidade_value = point.get('report', {}).get('categories', {}).get('mobilidade', 'N/D')
        visual_value = point.get('report', {}).get('categories', {}).get('visual', 'N/D')
        auditiva_value = point.get('report', {}).get('categories', {}).get('auditiva', 'N/D')
        geral_value = point.get('report', {}).get('categories', {}).get('geral', 'N/D')
        digital_value = point.get('report', {}).get('categories', {}).get('digital', 'N/D')
        cognitiva_value = point.get('report', {}).get('categories', {}).get('cognitiva', 'N/D')

        self.ids.detail_search_input.text = location_name
        self.ids.mobilidade_value.text = str(mobilidade_value)
        self.ids.visual_value.text = str(visual_value)
        self.ids.auditiva_value.text = str(auditiva_value)
        self.ids.geral_value.text = str(geral_value)
        self.ids.digital_value.text = str(digital_value)
        self.ids.cognitiva_value.text = str(cognitiva_value)

        mapview = self.ids.mapview_details
        lat = point.get('coordinates', {}).get('latitude')
        lon = point.get('coordinates', {}).get('longitude')
        if lat is None or lon is None:
            logger.warning(f"Coordenadas inválidas para {location_name}")
            return

        marker_images = {
            'green': 'marker_green.png',
            'red': 'marker_red.png',
            'yellow': 'marker_yellow.png'
        }
        color = point.get('color', 'red')
        marker_image = marker_images.get(color, 'marker_red.png')

        if not os.path.exists(marker_image):
            logger.warning(f"Imagem do marcador '{marker_image}' não encontrada. Usando marcador padrão.")
            marker = MapMarkerPopup(lat=lat, lon=lon)
        else:
            marker = MapMarkerPopup(lat=lat, lon=lon, source=marker_image)

        marker.point_data = point
        if self.current_marker:
            mapview.remove_widget(self.current_marker)
        self.current_marker = marker
        mapview.add_widget(marker)
        logger.info(f"Marcador de detalhes adicionado: {location_name} ({lat}, {lon}) com cor {color}")

        classification = point.get('classification', 'N/D')
        self.ids.report_label.text = f"Classificação: {classification}"

        self.ids.popup_title.text = location_name
        self.ids.popup_status.text = classification
        score = point.get('report', {}).get('score', 'N/D')
        self.ids.popup_rating.text = str(score)

        if isinstance(score, (int, float)):
            if score < 5:
                self.square_color = ACCENT_COLOR_RED
            elif 5 <= score < 10:
                self.square_color = ACCENT_COLOR_YELLOW
            else:
                self.square_color = ACCENT_COLOR_GREEN
        else:
            self.square_color = [1, 1, 1, 1]
            logger.warning(f"Score inválido para {location_name}: {score}")

    def search_location(self, text):
        logger.info(f"Pesquisando (na tela de detalhes) por: {text}")
        main_screen = self.manager.get_screen('main_screen')
        main_screen.ids.search_input.text = text 
        self.manager.current = 'main_screen'

class TurismoAcessivelApp(App):
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
        file_path = 'tourist_attractions.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.locations_data.append(line.split('|')[0])
            logger.info(f"Dados carregados de {file_path}: {len(self.locations_data)} locais encontrados.")
        except FileNotFoundError:
            logger.warning(f"Arquivo '{file_path}' não encontrado. A busca não funcionará.")

    def load_data_from_json(self):
        folder = 'results'
        self.points_data = []
        if not os.path.exists(folder):
            logger.warning(f"Pasta {folder} não encontrada.")
            return
        
        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                filepath = os.path.join(folder, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.points_data.append(data)
                        self.locations_data.append(data['name'])
                except Exception as e:
                    logger.error(f"Erro ao ler {filename}: {e}")
        logger.info(f"{len(self.points_data)} pontos carregados da pasta {folder}.")

if __name__ == '__main__':
    TurismoAcessivelApp().run()
