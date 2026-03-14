import os, hashlib, sys, random
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from plyer import notification
from kivy.core.window import Window

class LineParticle(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.width = random.uniform(30, 120)
        self.height = 1.5
        self.pos = (random.random() * Window.width, random.random() * Window.height)
        self.opacity = 0
        with self.canvas:
            self.color = Color(0, 0, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=(self.width, self.height))
        Clock.schedule_once(self.start_anim)

    def start_anim(self, dt):
        tx = self.x + (random.uniform(-1, 1) * 150)
        ty = self.y + (random.uniform(-1, 1) * 150)
        anim = Animation(pos=(tx, ty), width=self.width*1.5, opacity=0.3, duration=5, t='out_quad') + Animation(opacity=0, duration=2)
        anim.bind(on_complete=lambda *args: self.parent.remove_widget(self) if self.parent else None)
        anim.start(self)

    def on_pos(self, *args): self.rect.pos = self.pos
    def on_width(self, *args): self.rect.size = (self.width, self.height)
    def on_opacity(self, *args): self.color.a = self.opacity

class ModernSwitch(Button):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.text_label = text
        self.active = False
        self.background_normal = ""
        self.background_color = (0,0,0,0)
        self.circle_pos = 0.1
        with self.canvas.before:
            self.rect_color = Color(0.8, 0.8, 0.8, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.dot_color = Color(1, 1, 1, 1)
            self.dot = Rectangle(pos=self.pos, size=(0,0))
        self.label = Label(text=self.text_label, color=(0,0,0,1), bold=True)
        self.add_widget(self.label)
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = (self.x + self.width*0.7, self.y + self.height*0.35)
        self.rect.size = (self.width*0.2, self.height*0.3)
        self.label.pos = (self.x - self.width*0.1, self.y)
        self.label.size = self.size
        side = self.height * 0.25
        self.dot.size = (side, side)
        self.dot.pos = (self.rect.pos[0] + (self.rect.size[0] * self.circle_pos), self.rect.pos[1] + (self.rect.size[1]-side)/2)

    def set_state(self, state):
        self.active = state
        target_pos = 0.6 if self.active else 0.1
        target_color = (0.2, 0.8, 0.2, 1) if self.active else (0.8, 0.8, 0.8, 1)
        Animation(circle_pos=target_pos, duration=0.2).start(self)
        self.rect_color.rgba = target_color

class EvestApp(App):
    def build(self):
        self.title = "Evest Antivirus"
        self.auto_event = None
        self.root = FloatLayout()
        self.bg_layer = FloatLayout()
        self.root.add_widget(self.bg_layer)
        Clock.schedule_interval(self.spawn_line, 0.6)
        main = BoxLayout(orientation='vertical', padding=25, spacing=20)
        main.add_widget(Label(text="EVEST", font_size='45sp', bold=True, color=(0,0,0,1), size_hint_y=None, height=100))
        self.status = Label(text="СИСТЕМА ЗАЩИЩЕНА", color=(0,0,0,1), bold=True, size_hint_y=None, height=50)
        main.add_widget(self.status)
        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=15)
        main.add_widget(self.progress)
        self.btn_fast = Button(text="БЫСТРАЯ ПРОВЕРКА", background_normal='', background_color=(0,0,0,1), color=(1,1,1,1), size_hint_y=None, height=70)
        self.btn_fast.bind(on_press=self.scan)
        main.add_widget(self.btn_fast)
        self.sw_auto = ModernSwitch(text="АВТО-ПРОВЕРКА", size_hint_y=None, height=70)
        self.sw_auto.bind(on_press=self.auto_setup)
        main.add_widget(self.sw_auto)
        self.scroll = ScrollView()
        self.log_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.log_list.bind(minimum_height=self.log_list.setter('height'))
        self.scroll.add_widget(self.log_list)
        main.add_widget(self.scroll)
        self.root.add_widget(main)
        return self.root

    def spawn_line(self, dt): self.bg_layer.add_widget(LineParticle())

    def auto_setup(self, instance):
        if instance.active:
            if self.auto_event: self.auto_event.cancel()
            instance.set_state(False)
            return
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        self.slide = Slider(min=5, max=60, value=15, step=5)
        lbl = Label(text=f"Интервал: {int(self.slide.value)} мин", color=(1,1,1,1))
        self.slide.bind(value=lambda s, v: setattr(lbl, 'text', f"Интервал: {int(v)} мин"))
        btn = Button(text="ПОДТВЕРДИТЬ", size_hint_y=None, height=60)
        popup = Popup(title="Настройка времени", content=content, size_hint=(0.9, 0.4))
        content.add_widget(lbl); content.add_widget(self.slide); content.add_widget(btn)
        btn.bind(on_press=lambda x: self.confirm_auto(instance, popup))
        popup.open()

    def confirm_auto(self, instance, popup):
        interval = int(self.slide.value)
        self.auto_event = Clock.schedule_interval(self.scan, interval * 60)
        instance.set_state(True)
        popup.dismiss()

    def scan(self, *args):
        self.progress.value = 0
        self.status.text = "ПРОВЕРКА..."
        anim = Animation(value=100, duration=3)
        anim.bind(on_complete=self.finish_scan)
        anim.start(self.progress)

    def finish_scan(self, *args):
        self.status.text = "УГРОЗ НЕ НАЙДЕНО"
        try: notification.notify(title="Evest", message="Проверка завершена")
        except: pass

if __name__ == '__main__':
    Window.clearcolor = (1, 1, 1, 1)
    EvestApp().run()
