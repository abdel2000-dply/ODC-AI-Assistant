from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.lang import Builder

Builder.load_string('''
<AssistantUI>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        padding: [20, 40]  # Increased vertical padding
        spacing: 20  # Increased spacing

        # ODC Logo and Title
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            Label:
                text: 'ODC AI Assistant'
                font_size: '36sp'
                bold: True
                color: 1, 0.5, 0, 1
                size_hint_y: None
                height: self.texture_size[1]
                pos_hint: {'center_x': 0.5}

        # Status Display
        Label:
            id: status_label
            text: root.status_text
            font_size: '24sp'
            size_hint_y: 0.1
            color: 0.5, 0.8, 1, 1
            pos_hint: {'center_x': 0.5}

        # Language Selection
        BoxLayout:
            size_hint_y: 0.1
            size_hint_x: 0.8
            pos_hint: {'center_x': 0.5}
            spacing: 20
            
            Button:
                text: 'English'
                background_normal: ''
                background_color: (0.2, 0.6, 1, 1) if root.current_lang == 'en' else (0.3, 0.3, 0.3, 1)
                on_press: root.set_language('en')
            
            Button:
                text: 'Français'
                background_normal: ''
                background_color: (0.2, 0.6, 1, 1) if root.current_lang == 'fr' else (0.3, 0.3, 0.3, 1)
                on_press: root.set_language('fr')
            
            Button:
                text: 'العربية'
                background_normal: ''
                background_color: (0.2, 0.6, 1, 1) if root.current_lang == 'ar' else (0.3, 0.3, 0.3, 1)
                on_press: root.set_language('ar')

        # Chat History
        ScrollView:
            size_hint_y: 0.45
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5}
            BoxLayout:
                id: chat_history
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 15
                padding: [20, 10]

        # Recording Button and Animation
        BoxLayout:
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 10
            
            Label:
                id: animation_label
                text: root.animation_dots
                font_size: '48sp'
                color: 1, 0, 0, 1 if root.is_recording else (1, 0.5, 0, 1)
                size_hint_y: None
                height: '48sp'
            
            Button:
                id: rec_button
                text: 'Click to Start Recording' if not root.is_recording else 'Click to Stop Recording'
                size_hint: None, None
                size: 300, 80
                pos_hint: {'center_x': 0.5}
                background_normal: ''
                background_color: (1, 0, 0, 1) if root.is_recording else (1, 0.5, 0, 1)
                on_press: root.toggle_recording()
''')

class AssistantUI(BoxLayout):
    status_text = StringProperty('Ready')
    animation_dots = StringProperty('')
    current_lang = StringProperty('en')
    is_recording = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation_event = None
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
        self.is_recording = not self.is_recording
        
    def start_recording(self):
        self.status_text = 'Recording...'
        self.animation_event = Clock.schedule_interval(self.update_animation, 0.5)
        
    def stop_recording(self):
        self.status_text = 'Processing...'
        if self.animation_event:
            self.animation_event.cancel()
        self.animation_dots = ''
        Clock.schedule_once(lambda dt: self.reset_status(), 2)
    
    def reset_status(self):
        self.status_text = 'Ready'

    def update_animation(self, dt):
        dots = len(self.animation_dots)
        self.animation_dots = '.' * ((dots + 1) % 4)
        
    def add_message(self, text, is_user=True):
        msg = Label(
            text=text,
            size_hint_y=None,
            height=self.minimum_height,
            text_size=(self.width * 0.7, None),
            halign='right' if is_user else 'left',
            valign='middle',
            color=(0.2, 0.6, 1, 1) if is_user else (1, 0.5, 0, 1),
            pos_hint={'right': 0.95} if is_user else {'x': 0.05}
        )
        self.ids.chat_history.add_widget(msg)

class AssistantApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return AssistantUI()

if __name__ == '__main__':
    AssistantApp().run()