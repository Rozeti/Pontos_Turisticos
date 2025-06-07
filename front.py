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

        Label:
            text: 'Mapa Interativo (integrado com Folium)'
            color: app.text_color
            pos_hint: {'center_x': 0.5, 'center_y': 0.2}
            size_hint: (1, 0.4)
            canvas.before:
                Color:
                    rgb: app.secondary_color
                Rectangle:
                    pos: self.pos
                    size: self.size


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
                            text: 'Rampas para cadeirantes'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: rampas_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Pista tátil'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: pista_tatil_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Cão Guia'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: cao_guia_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Elevadores'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: elevadores_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'

                    # Seção de Segurança
                    Label:
                        text: 'Segurança'
                        color: app.text_color
                        font_size: '20sp'
                        bold: True
                        size_hint_y: None
                        height: dp(30)
                        text_size: self.size
                        valign: 'middle'

                    GridLayout:
                        id: security_grid
                        cols: 2
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(10)
                        row_default_height: dp(30)
                        row_force_default: True
                        Label:
                            text: 'Bombeiros'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: bombeiros_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Seguranças'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: segurancas_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Câmeras'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: cameras_value_label
                            text: 'N/D'
                            halign: 'right'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            text: 'Casos de crimes'
                            color: app.text_color
                            halign: 'left'
                            text_size: self.size
                            valign: 'middle'
                        Label:
                            id: crimes_value_label
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
                Label:
                    text: 'Mapa Interativo com Pontos Turísticos'
                    color: app.text_color
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    font_size: '20sp'
                    bold: True
                BoxLayout:
                    id: map_popup
                    orientation: 'vertical'
                    size_hint: (0.4, 0.2)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.7}
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


class DetailScreen(Screen):
    """
    Tela para exibir detalhes de um ponto turístico.
    """
    # REMOVIDO o método on_enter, pois não é mais necessário carregar um exemplo padrão
    
    # MÉTODO RENOMEADO E MODIFICADO
    def load_details(self, location_name):
        """
        Carrega os detalhes de um local específico na tela.
        Como não temos os dados detalhados, preenche os campos com 'N/D'.
        """
        # Preenche o nome do local
        self.ids.detail_search_input.text = location_name
        
        # Define todos os valores de detalhes como "Não Disponível"
        self.ids.rampas_value_label.text = 'N/D'
        self.ids.rampas_value_label.color = TEXT_COLOR
        
        self.ids.pista_tatil_value_label.text = 'N/D'
        self.ids.pista_tatil_value_label.color = TEXT_COLOR
        
        self.ids.cao_guia_value_label.text = 'N/D'
        self.ids.cao_guia_value_label.color = TEXT_COLOR

        self.ids.elevadores_value_label.text = 'N/D'
        self.ids.elevadores_value_label.color = TEXT_COLOR

        self.ids.bombeiros_value_label.text = 'N/D'
        self.ids.bombeiros_value_label.color = TEXT_COLOR

        self.ids.segurancas_value_label.text = 'N/D'
        self.ids.segurancas_value_label.color = TEXT_COLOR

        self.ids.cameras_value_label.text = 'N/D'
        self.ids.cameras_value_label.color = TEXT_COLOR

        self.ids.crimes_value_label.text = 'N/D'
        self.ids.crimes_value_label.color = TEXT_COLOR

        # Limpa e atualiza o relatório
        self.ids.report_label.text = f"Relatório detalhado para '{location_name}' ainda não disponível."
        
        # Atualiza o pop-up do mapa
        self.ids.popup_title.text = location_name
        self.ids.popup_status.text = "Status Indisponível"
        self.ids.popup_rating.text = "N/D"

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

    def build(self):
        self.title = 'Turismo Acessível DF'
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


if __name__ == '__main__':
    # Para o aplicativo funcionar, você deve fornecer os seguintes arquivos de imagem
    # no mesmo diretório que o seu script Python:
    # 1. logo_turseguro.png
    # 2. search_icon.png
    # 3. star_icon.png
    
    TurismoAcessivelApp().run()
