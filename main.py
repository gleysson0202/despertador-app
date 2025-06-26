from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.video import Video
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime
from plyer import filechooser
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import platform

class AlarmVideoApp(App):
    def build(self):
        if platform != 'android':
            Window.fullscreen = True

        self.video = None
        self.alarm_hour = 0
        self.alarm_minute = 0
        self.video_path = None

        layout = BoxLayout(orientation='vertical')

        # Botão para selecionar vídeo
        select_button = Button(text="Selecionar Vídeo", size_hint_y=0.1)
        select_button.bind(on_press=self.select_video)
        layout.add_widget(select_button)

        self.selected_label = Label(text="Nenhum vídeo selecionado", size_hint_y=0.1)
        layout.add_widget(self.selected_label)

        # Seletor de hora
        time_selector = BoxLayout(size_hint_y=0.2)

        self.hour_label = Label(text='Hora: 00', size_hint_x=0.3)
        self.min_label = Label(text='Minuto: 00', size_hint_x=0.3)

        hour_up = Button(text='Hora +', on_press=self.increase_hour)
        hour_down = Button(text='Hora -', on_press=self.decrease_hour)
        min_up = Button(text='Minuto +', on_press=self.increase_min)
        min_down = Button(text='Minuto -', on_press=self.decrease_min)

        time_selector.add_widget(hour_up)
        time_selector.add_widget(hour_down)
        time_selector.add_widget(self.hour_label)
        time_selector.add_widget(min_up)
        time_selector.add_widget(min_down)
        time_selector.add_widget(self.min_label)

        layout.add_widget(time_selector)

        # Botão para iniciar o alarme
        start_button = Button(text='Ativar Alarme com este Vídeo', size_hint_y=0.1)
        start_button.bind(on_press=self.start_alarm)
        layout.add_widget(start_button)

        return layout

    def select_video(self, instance):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        filechooser.open_file(on_selection=self.on_file_selection)

    def on_file_selection(self, selection):
        if selection:
            self.video_path = selection[0]
            self.selected_label.text = f"Selecionado: {self.video_path.split('/')[-1]}"
            print(f"Vídeo selecionado: {self.video_path}")
        else:
            self.selected_label.text = "Nenhum vídeo selecionado"

    def increase_hour(self, instance):
        self.alarm_hour = (self.alarm_hour + 1) % 24
        self.hour_label.text = f'Hora: {self.alarm_hour:02d}'

    def decrease_hour(self, instance):
        self.alarm_hour = (self.alarm_hour - 1) % 24
        self.hour_label.text = f'Hora: {self.alarm_hour:02d}'

    def increase_min(self, instance):
        self.alarm_minute = (self.alarm_minute + 1) % 60
        self.min_label.text = f'Minuto: {self.alarm_minute:02d}'

    def decrease_min(self, instance):
        self.alarm_minute = (self.alarm_minute - 1) % 60
        self.min_label.text = f'Minuto: {self.alarm_minute:02d}'

    def start_alarm(self, instance):
        if not self.video_path:
            print("Nenhum vídeo selecionado.")
            return

        print(f"Alarme definido para {self.alarm_hour:02d}:{self.alarm_minute:02d}")
        Clock.schedule_interval(self.check_time, 1)

    def check_time(self, dt):
        now = datetime.now()
        if now.hour == self.alarm_hour and now.minute == self.alarm_minute:
            Clock.unschedule(self.check_time)
            self.play_video()

    def play_video(self):
        Window.clear()
        self.video = Video(source=self.video_path,
                           state='play',
                           options={'eos': 'loop'},
                           volume=1)

        self.video.allow_stretch = True
        self.video.keep_ratio = False
        self.video.opacity = 1

        root = FloatLayout()
        root.add_widget(self.video)
        App.get_running_app().root_window.clear_widgets()
        App.get_running_app().root_window.add_widget(root)

if __name__ == '__main__':
    AlarmVideoApp().run()
