import os
import wave
import pyaudio
import sounddevice as sd
import numpy as np
import noisereduce as nr
import scipy.io.wavfile as wav
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from src.utils.utils import transcribe_audio_with_groq, recognize_speech_from_mic, speak  # Import updated functions
from src.assistant import LangChainHandler
import asyncio

Builder.load_string('''
<AssistantUI>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1  # Darkest dark background
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        padding: [20, 30]
        spacing: 15

        # ODC Logo and Title
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'horizontal'
            spacing: 10
            Image:
                source: 'src/ui/Assets/orange_master_logo.png'  # Use PNG file instead of SVG
                size_hint: None, None
                size: 50, 50
                allow_stretch: True
            Label:
                text: 'ODC AI Assistant'
                font_size: '40sp'
                bold: True
                font_name: 'Roboto'
                color: 1, 0.5, 0, 1
                size_hint_y: None
                height: self.texture_size[1]
                pos_hint: {'center_x': 0.5}

        # Status Display
        BoxLayout:
            size_hint_y: 0.08
            orientation: 'horizontal'
            padding: [20, 0]
            Label:
                text: root.status_text
                font_size: '20sp'
                color: (0.7, 0.7, 0.7, 1) # light gray
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            
            # Recording status Icon
            Label:
                text: '●' if root.is_recording else ''
                font_size: '24sp'
                color: 1, 0, 0, 1 # Red
                size_hint_x: None
                width: 20
                pos_hint: {'center_y': 0.5}
                

        # Language Selection
        BoxLayout:
            size_hint_y: 0.12
            size_hint_x: 0.6
            pos_hint: {'center_x': 0.5}
            spacing: 15
            Button:
                text: root.current_lang
                on_release: root.show_language_dropdown()
                background_normal: ''
                background_color: (0.3, 0.3, 0.3, 1) # Dark Gray
                color: (1, 0.913, 0.788, 1) # Blanched Almond
                font_size: '20sp'

        # Chat History
        ScrollView:
            size_hint_y: 0.45
            size_hint_x: 0.9
            pos_hint: {'center_x': 0.5}
            scroll_type: ['content']
            effect_cls: 'ScrollEffect'
            touch_mode: 'scroll'  # added this
            multitouch_sim: False  # added this
            BoxLayout:
                id: chat_history
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 15
                padding: [15, 10]

        # Recording Button and Animation
        BoxLayout:
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 10
            
            Widget: # Recording Visualizer Container
                size_hint: None, None
                size: 60, 60
                pos_hint: {'center_x': 0.5}
                
                canvas:
                    Color:
                        rgba: (1, 0, 0, 0.8) if root.is_recording else (1, 0.5, 0, 0.8) # Red/Orange
                    Ellipse:
                        pos: self.x + 5, self.y + 5
                        size: self.width - 10, self.height - 10
                        angle_start: 0
                        angle_end: root.visualizer_angle

            Button:
                id: rec_button
                text: 'Start Recording' if not root.is_recording else 'Stop Recording'
                size_hint: None, None
                size: 250, 70
                pos_hint: {'center_x': 0.5}
                background_normal: ''
                background_color: (1, 0, 0, 1) if root.is_recording else (1, 0.5, 0, 1)  # Red/Orange
                font_size: '20sp'

                on_press: root.toggle_recording()

<MessageBubble@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: [10, 10, 10, 10]
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15, 15, 15, 15]

    Label:
        id: msg_label
        text: ''
        text_size: root.width * 0.8, None
        size_hint_y: None
        height: self.texture_size[1]
        color: 0,0,0,1 # Black
        halign: 'left' if root.is_user else 'right'
        valign: 'middle'
        font_size: '18sp'
''')

class MessageBubble(BoxLayout):
    bg_color = (1, 0.913, 0.788, 0.8) # Blanched Almond with some transparency
    is_user = BooleanProperty(False)

class AssistantUI(BoxLayout):
    status_text = StringProperty('Ready')
    current_lang = StringProperty('English')
    is_recording = BooleanProperty(False)
    visualizer_angle = NumericProperty(0)  # For the recording animation
    
    languages = ['English', 'French', 'Arabic']
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation_event = None
        self.visualizer_animation = None  # To store the visualizer animation
        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Set background to dark black
        self.audio_frames = []
        self.langchain_handler = LangChainHandler()
        
        # set lang to default value
        self.set_current_lang(self.langchain_handler.selected_language)

        # Create Dropdown for languages
        self.language_dropdown = DropDown()
        for lang in self.languages:
            btn = Button(text=lang, size_hint_y=None, height=40, background_normal='',background_color= (0.3, 0.3, 0.3, 1))
            btn.bind(on_release=lambda btn, l=lang: self.language_selection(l))
            self.language_dropdown.add_widget(btn)
    
    def set_current_lang(self, lang):
        for key, value in self.langchain_handler.SUPPORTED_LANGUAGES.items():
            if value['code'] == lang:
                self.current_lang = value['name']
                break

    def show_language_dropdown(self):
        self.language_dropdown.open(self.children[0].children[1].children[0])
    
    def language_selection(self, lang):
        self.current_lang = lang
        for key, value in self.langchain_handler.SUPPORTED_LANGUAGES.items():
            if value['name'] == lang:
                self.langchain_handler.selected_language = value['code']
                break
        self.language_dropdown.dismiss()

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
        self.is_recording = not self.is_recording

    def start_recording(self):
        self.status_text = 'Recording...'
        self.start_visualizer_animation()
        self.audio_frames = []
        self.audio_stream = sd.InputStream(samplerate=44100, channels=1, dtype='int16', callback=self.audio_callback)
        self.audio_stream.start()

    def audio_callback(self, indata, frames, time, status):
        self.audio_frames.append(indata.copy())

    def stop_recording(self):
        self.status_text = 'Processing...'
        self.stop_visualizer_animation()
        self.audio_stream.stop()
        self.audio_stream.close()
        self.save_audio_to_file()
        Clock.schedule_once(lambda dt: asyncio.run(self.process_audio()), 1)

    def save_audio_to_file(self, file_name="live_audio.wav"):
        audio_data = np.concatenate(self.audio_frames, axis=0).flatten()
        
        # Apply noise reduction
        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=44100)
        
        # Amplify the audio
        amplified_audio = (reduced_noise_audio / np.max(np.abs(reduced_noise_audio))).astype(np.float64)

        wav.write(file_name, 44100, amplified_audio)
        print(f"Recording saved as '{file_name}'.")

    async def process_audio(self):
        question = transcribe_audio_with_groq(audio_file="live_audio.wav", language=self.langchain_handler.selected_language)
        if not question:
            print("using speech recognition instead")
            question = recognize_speech_from_mic(language=self.langchain_handler.selected_language)
        if question:
             self.add_message(question, is_user=True)
             response = await asyncio.to_thread(self.langchain_handler.get_response, question)
             self.add_message(response['answer'], is_user=False)
             await speak(response['answer'], lang=self.langchain_handler.selected_language)

        self.reset_status()

    def reset_status(self):
        self.status_text = 'Ready'

    def start_visualizer_animation(self):
        self.visualizer_animation = Animation(visualizer_angle=360, duration=2)
        self.visualizer_animation.repeat = True  # Set repeat attribute correctly
        self.visualizer_animation.start(self)

    def stop_visualizer_animation(self):
        if self.visualizer_animation:
            self.visualizer_animation.stop(self)
            self.visualizer_angle = 0

    def add_message(self, text, is_user=True):
        bubble = MessageBubble(is_user=is_user)
        bubble.ids.msg_label.text = text
        bubble.bg_color = (1, 0.913, 0.788, 0.8) if is_user else (1, 0.5, 0, 0.8)
        self.ids.chat_history.add_widget(bubble)

class AssistantApp(App):
    def build(self):
        Window.size = (640, 480)  # Set the window size to match the 3.5" display resolution
        Window.fullscreen = True  # Enable fullscreen mode
        print("Building AssistantUI...")
        
        # Force Kivy to refresh input configuration (touch events)
        from kivy.config import Config
        import os
        
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

        if os.path.exists(config_path):
           Config.read(config_path)
           Config.set('input', 'mouse', 'mouse')
           Config.set('kivy', 'window_size', '640x480')
           Config.set('kivy', 'window_icon', 'None')
           Config.write()
        else:
            print(f"Config file not found at {config_path}")
        
        return AssistantUI()

if __name__ == '__main__':
    print("Running AssistantApp...")
    AssistantApp().run()
    print("AssistantApp finished.")