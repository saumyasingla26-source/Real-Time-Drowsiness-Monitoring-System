from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.metrics import dp
import numpy as np


class GraphScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._last_fig_data = None
        self.build_ui()

    def build_ui(self):

        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(15))

        with root.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
            Color(0.7, 0.2, 1, 0.15)
            self.glow1 = Ellipse(pos=(-120, 450), size=(340, 340))
            Color(0.1, 0.7, 1, 0.12)
            self.glow2 = Ellipse(pos=(250, -120), size=(420, 420))

        root.bind(pos=self.update_bg, size=self.update_bg)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.09), spacing=dp(10))

        home_btn = Button(
            text="⌂ Home", size_hint=(0.28, 1), font_size=dp(14), bold=True,
            background_normal='', background_color=(0, 0, 0, 0), color=(1, 1, 1, 1)
        )

        with home_btn.canvas.before:
            Color(0.55, 0.25, 1, 1)
            self.home_bg = RoundedRectangle(pos=home_btn.pos, size=home_btn.size, radius=[18])

        home_btn.bind(
            pos=lambda inst, val: setattr(self.home_bg, 'pos', val),
            size=lambda inst, val: setattr(self.home_bg, 'size', val)
        )
        home_btn.bind(on_press=lambda x: self.go_home())

        title = Label(text='[b]EAR TREND ANALYSIS[/b]', markup=True, font_size=dp(24), color=(1, 1, 1, 1))

        top_bar.add_widget(home_btn)
        top_bar.add_widget(title)

        graph_card = BoxLayout(orientation='vertical', padding=dp(12), size_hint=(1, 0.68))

        with graph_card.canvas.before:
            Color(0.13, 0.14, 0.24, 0.93)
            self.graph_bg = RoundedRectangle(pos=graph_card.pos, size=graph_card.size, radius=[28])
            Color(0.1, 0.8, 1, 0.4)
            self.graph_border = Line(
                rounded_rectangle=(graph_card.x, graph_card.y, graph_card.width, graph_card.height, 28),
                width=1.5
            )

        graph_card.bind(pos=self.update_graph_card, size=self.update_graph_card)

        self.graph_image = KivyImage(allow_stretch=True, keep_ratio=True)
        graph_card.add_widget(self.graph_image)

        analytics_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(12), size_hint=(1, 0.16))

        with analytics_card.canvas.before:
            Color(0.12, 0.13, 0.22, 0.95)
            self.analytics_bg = RoundedRectangle(pos=analytics_card.pos, size=analytics_card.size, radius=[24])

        analytics_card.bind(pos=self.update_analytics_card, size=self.update_analytics_card)

        self.info_lbl = Label(text="Frames: 0 | Avg EAR: 0.000", font_size=dp(18), bold=True, color=(0.1, 0.85, 1, 1))
        self.status_info = Label(text="Monitoring eye activity trends", font_size=dp(13), color=(0.8, 0.8, 0.9, 1))

        analytics_card.add_widget(self.info_lbl)
        analytics_card.add_widget(self.status_info)

        bottom_nav = GridLayout(cols=2, spacing=dp(12), size_hint=(1, 0.09))

        dash_btn = self.create_nav_button("LIVE DASHBOARD", (0.1, 0.7, 1, 1))
        hist_btn = self.create_nav_button("HISTORY", (1, 0.35, 0.45, 1))

        dash_btn.bind(on_press=lambda x: self.change_screen('dashboard'))
        hist_btn.bind(on_press=lambda x: self.change_screen('history'))

        bottom_nav.add_widget(dash_btn)
        bottom_nav.add_widget(hist_btn)

        root.add_widget(top_bar)
        root.add_widget(graph_card)
        root.add_widget(analytics_card)
        root.add_widget(bottom_nav)

        self.add_widget(root)

    def create_nav_button(self, text, color_theme):

        btn = Button(
            text=text, font_size=dp(14), bold=True,
            background_normal='', background_color=(0, 0, 0, 0), color=(1, 1, 1, 1)
        )

        with btn.canvas.before:
            Color(*color_theme)
            bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[18])

        btn.bind(
            pos=lambda inst, val: setattr(bg, 'pos', val),
            size=lambda inst, val: setattr(bg, 'size', val)
        )

        return btn

    def update_bg(self, *args):
        self.bg.pos = self.children[0].pos
        self.bg.size = self.children[0].size

    def update_graph_card(self, *args):
        c = self.children[0].children[2]
        self.graph_bg.pos = c.pos
        self.graph_bg.size = c.size
        self.graph_border.rounded_rectangle = (c.x, c.y, c.width, c.height, 28)

    def update_analytics_card(self, *args):
        c = self.children[0].children[1]
        self.analytics_bg.pos = c.pos
        self.analytics_bg.size = c.size

    def go_home(self):
        self.manager.current = 'home'

    def change_screen(self, screen):
        self.manager.current = screen

    def on_enter(self, *args):
        app = self.get_app()
        if app and hasattr(app, 'detector'):
            if app.detector.history:
                self.update_graph(app.detector.history[:])

    def get_app(self):
        try:
            from kivy.app import App
            return App.get_running_app()
        except:
            return None

    def update_graph(self, ear_history):

        if len(ear_history) < 2:
            self.info_lbl.text = "Not enough data"
            return

        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(8, 4), facecolor='#0B0B18')
            ax.set_facecolor('#0B0B18')

            ax.grid(color='#222244', linestyle='--', linewidth=0.5, alpha=0.5)
            ax.plot(ear_history, color='#00D4FF', linewidth=3)
            ax.axhline(y=0.25, color='#FF3B5C', linestyle='--', linewidth=2, label='Drowsy Threshold')

            ax.set_title("EAR OVER TIME", color='white', fontsize=18, fontweight='bold')
            ax.set_xlabel("Frame Number", color='#AAAAAA', fontsize=10)
            ax.set_ylabel("EAR Value", color='#AAAAAA', fontsize=10)
            ax.set_ylim(0, 0.7)
            ax.tick_params(colors='#BBBBBB', labelsize=9)

            for sp in ax.spines.values():
                sp.set_color('#444466')

            leg = ax.legend(facecolor='#111122', edgecolor='#555577', fontsize=9)
            for txt in leg.get_texts():
                txt.set_color("white")

            fig.tight_layout(pad=2)
            fig.canvas.draw()

            wd, ht = fig.canvas.get_width_height()
            arr = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(ht, wd, 4)
            arr = arr[:, :, :3]

            self._last_fig_data = (arr.copy(), wd, ht)
            arr = np.flipud(arr)

            tex = Texture.create(size=(wd, ht), colorfmt='rgb')
            tex.blit_buffer(arr.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.graph_image.texture = tex

            avg_ear = round(sum(ear_history) / len(ear_history), 3)
            mn = round(min(ear_history), 3)

            self.info_lbl.text = f"Frames: {len(ear_history)}   |   Avg EAR: {avg_ear}"

            if mn < 0.25:
                self.status_info.text = "⚠ Drowsiness patterns detected"
                self.status_info.color = (1, 0.3, 0.4, 1)
            else:
                self.status_info.text = "✓ Driver appears attentive"
                self.status_info.color = (0.2, 1, 0.5, 1)

            plt.close(fig)

        except Exception as err:
            print("Graph error:", err)
            self.info_lbl.text = f"Graph Error: {err}"