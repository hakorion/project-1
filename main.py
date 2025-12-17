# Romantic Game
# Kivy / Android (Buildozer Ready)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Triangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
import random

HER_NAME = "Cherry Lau"
Window.clearcolor = (0.04, 0.03, 0.08, 1)

# ---------------- TYPEWRITER LABEL ----------------
class TypewriterLabel(Label):
    def __init__(self, text_to_type="", speed=0.04, on_finish=None, **kwargs):
        super().__init__(**kwargs)
        self.full_text = text_to_type
        self.text = ""
        self.index = 0
        self.on_finish = on_finish
        Clock.schedule_interval(self._type, speed)

    def _type(self, dt):
        if self.index < len(self.full_text):
            self.text += self.full_text[self.index]
            self.index += 1
        else:
            if self.on_finish:
                Clock.schedule_once(lambda dt: self.on_finish(), 0.8)
            return False

# ---------------- FIREWORK ----------------
class Firework(Widget):
    def __init__(self, pos, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (6, 6)
        self.center = pos

        with self.canvas:
            Color(random.random(), random.random(), random.random())
            self.dot = Ellipse(pos=self.pos, size=self.size)

        anim = Animation(
            x=self.x + random.uniform(-160, 160),
            y=self.y + random.uniform(-160, 160),
            opacity=0,
            duration=1.4
        )
        anim.bind(on_complete=lambda *x: self.parent and self.parent.remove_widget(self))
        anim.start(self)

# ---------------- HEART ----------------
class Heart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (42, 42)

        self.pos = (
            random.randint(60, int(Window.width - 60)),
            random.randint(160, int(Window.height - 160))
        )

        self.dy = random.uniform(0.2, 0.35)

        with self.canvas:
            Color(1, 0.4, 0.6)
            self.l = Ellipse()
            self.r = Ellipse()
            self.t = Triangle()

        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.update_graphics()
        Clock.schedule_interval(self.float_up, 1 / 60)

    def update_graphics(self, *args):
        x, y = self.pos
        w, h = self.size
        r = w * 0.5

        self.l.size = self.r.size = (r, r)
        self.l.pos = (x, y + h * 0.35)
        self.r.pos = (x + r * 0.9, y + h * 0.35)

        self.t.points = [
            x, y + h * 0.6,
            x + w, y + h * 0.6,
            x + w / 2, y
        ]

    def float_up(self, dt):
        self.y += self.dy
        if self.y > Window.height + 40:
            self.y = -40

    def pop(self):
        anim = Animation(opacity=0, duration=0.15)
        anim.bind(on_complete=lambda *x: self.finish())
        anim.start(self)

    def finish(self):
        app = App.get_running_app()
        app.root.get_screen('game').collected()
        if self.parent:
            self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pop()
            return True
        return super().on_touch_down(touch)

# ---------------- SCREENS ----------------
class IntroScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=60, spacing=40)

        layout.add_widget(TypewriterLabel(
            text_to_type=f"Hey {HER_NAME}.\n\nI made something just for you.",
            font_size='26sp',
            halign='center'
        ))

        btn = Button(text="Continue", size_hint=(1, 0.2))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'story'))
        layout.add_widget(btn)
        self.add_widget(layout)

class StoryScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=60, spacing=35)

        layout.add_widget(TypewriterLabel(
            text_to_type=(
                f"{HER_NAME},\n\n"
                "Every heart you collect is a small reminder\n"
                "of how important you are to me."
            ),
            font_size='20sp',
            halign='center'
        ))

        btn = Button(text="Start", size_hint=(1, 0.2))
        btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'game'))
        layout.add_widget(btn)
        self.add_widget(layout)

class MiniGameScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.collected_count = 0
        self.layout = FloatLayout()

        self.layout.add_widget(Label(
            text="Collect the hearts",
            font_size='22sp',
            pos_hint={'center_x': 0.5, 'top': 1}
        ))

        for _ in range(5):
            self.layout.add_widget(Heart())

        self.add_widget(self.layout)

    def collected(self):
        self.collected_count += 1
        if self.collected_count >= 5:
            self.manager.current = 'confession'

# ---------------- CONFESSION ----------------
class ConfessionScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.step = 0

        self.layout = BoxLayout(orientation='vertical', padding=55, spacing=35)
        self.add_widget(self.layout)

        self.yes_btn = Button(text="Yes", size_hint=(1, 0.2), opacity=0)
        self.no_btn = Button(text="No", size_hint=(1, 0.2), opacity=0)

        self.yes_btn.bind(on_release=self.next_step)
        self.no_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'no'))

        self.show_text()

        self.layout.add_widget(self.yes_btn)
        self.layout.add_widget(self.no_btn)

    def show_text(self):
        message = (
            f"{HER_NAME}...\n\n"
            "From the moment you became part of my life,\n"
            "everything started to feel a little warmer.\n\n"
            "I like the way you make ordinary days feel special.\n"
            "I like how being with you feels natural.\n\n"
            "So I just want to ask you something important.\n\n"
            "Will you be my girlfriend?"
        )

        self.label = TypewriterLabel(
            text_to_type=message,
            font_size='22sp',
            halign='center',
            on_finish=self.reveal_buttons
        )
        self.layout.add_widget(self.label, index=0)

    def reveal_buttons(self):
        Animation(opacity=1, duration=0.6).start(self.yes_btn)
        Animation(opacity=1, duration=0.6).start(self.no_btn)

    def next_step(self, instance):
        self.step += 1
        if self.step == 1:
            self.label.text = "Are you sure?"
        elif self.step == 2:
            self.label.text = "Oh, so you really want me?"
        elif self.step == 3:
            self.manager.current = 'yes'

# ---------------- END YES (WITH FIREWORKS) ----------------
class EndYes(Screen):
    def on_enter(self):
        self.clear_widgets()

        self.label = TypewriterLabel(
            text_to_type=(
                "You made me the happiest man alive right now.\n\n"
                "I cannot wait to make more memories with you."
            ),
            font_size='26sp',
            halign='center',
            on_finish=self.start_fireworks
        )
        self.add_widget(self.label)

    def start_fireworks(self):
        Clock.schedule_interval(self.spawn_fireworks, 0.35)

    def spawn_fireworks(self, dt):
        for _ in range(10):
            self.add_widget(Firework(
                pos=(random.randint(0, Window.width),
                     random.randint(0, Window.height))
            ))

class EndNo(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.add_widget(TypewriterLabel(
            text_to_type=f"Thank you for being honest, {HER_NAME}.",
            font_size='24sp',
            halign='center'
        ))

# ---------------- APP ----------------
class RomanticApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(StoryScreen(name='story'))
        sm.add_widget(MiniGameScreen(name='game'))
        sm.add_widget(ConfessionScreen(name='confession'))
        sm.add_widget(EndYes(name='yes'))
        sm.add_widget(EndNo(name='no'))
        return sm

if __name__ == '__main__':
    RomanticApp().run()
