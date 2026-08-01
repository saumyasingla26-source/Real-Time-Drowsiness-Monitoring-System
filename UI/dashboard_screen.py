from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.metrics import dp


class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):

        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(15))

        with root.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
            Color(0.7, 0.2, 1, 0.15)
            self.glow1 = Ellipse(pos=(-100, 450), size=(320, 320))
            Color(0.1, 0.7, 1, 0.12)
            self.glow2 = Ellipse(pos=(250, -100), size=(420, 420))

        root.bind(pos=self._update_bg, size=self._update_bg)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.09), spacing=dp(10))

        home_btn = Button(
            text="⌂ Home",
            size_hint=(0.28, 1),
            font_size=dp(14),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )

        with home_btn.canvas.before:
            Color(0.55, 0.25, 1, 1)
            self.home_bg = RoundedRectangle(pos=home_btn.pos, size=home_btn.size, radius=[18])

        home_btn.bind(
            pos=lambda inst, val: setattr(self.home_bg, 'pos', val),
            size=lambda inst, val: setattr(self.home_bg, 'size', val)
        )
        home_btn.bind(on_press=lambda x: self._go_to('home'))

        title = Label(text='[b]LIVE DASHBOARD[/b]', markup=True, font_size=dp(24), color=(1, 1, 1, 1))

        top_bar.add_widget(home_btn)
        top_bar.add_widget(title)

        cam_wrap = BoxLayout(orientation='vertical', padding=dp(10), size_hint=(1, 0.58))

        with cam_wrap.canvas.before:
            Color(0.13, 0.14, 0.24, 0.92)
            self.camera_bg = RoundedRectangle(pos=cam_wrap.pos, size=cam_wrap.size, radius=[28])
            Color(0.2, 0.8, 1, 0.4)
            self.camera_border = Line(
                rounded_rectangle=(cam_wrap.x, cam_wrap.y, cam_wrap.width, cam_wrap.height, 28),
                width=1.5
            )

        cam_wrap.bind(pos=self.update_camera_card, size=self.update_camera_card)

        self.cam_feed = KivyImage(allow_stretch=True, keep_ratio=True)
        cam_wrap.add_widget(self.cam_feed)

        self.status_card = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(15), size_hint=(1, 0.22))

        with self.status_card.canvas.before:
            Color(0.12, 0.13, 0.22, 0.95)
            self.status_bg = RoundedRectangle(pos=self.status_card.pos, size=self.status_card.size, radius=[26])

        self.status_card.bind(pos=self.update_status_card, size=self.update_status_card)

        self.status_lbl = Label(
            text='[b]WAITING[/b]', markup=True, font_size=dp(32),
            bold=True, color=(1, 0.8, 0.1, 1), size_hint=(1, 0.5)
        )

        stats_grid = GridLayout(cols=2, spacing=dp(12), size_hint=(1, 0.5))

        self.ear_box = self.create_stat_card("EAR VALUE", "0.000", (0.1, 0.8, 1, 1))
        self.alert_box = self.create_stat_card("ALERTS", "0", (1, 0.3, 0.45, 1))

        stats_grid.add_widget(self.ear_box)
        stats_grid.add_widget(self.alert_box)

        self.status_card.add_widget(self.status_lbl)
        self.status_card.add_widget(stats_grid)

        nav = GridLayout(cols=2, spacing=dp(12), size_hint=(1, 0.10))

        graph_btn = self.create_nav_button("EAR GRAPH", (0.1, 0.7, 1, 1))
        history_btn = self.create_nav_button("HISTORY", (1, 0.4, 0.5, 1))

        graph_btn.bind(on_press=lambda x: self._go_to('graph'))
        history_btn.bind(on_press=lambda x: self._go_to('history'))

        nav.add_widget(graph_btn)
        nav.add_widget(history_btn)

        root.add_widget(top_bar)
        root.add_widget(cam_wrap)
        root.add_widget(self.status_card)
        root.add_widget(nav)

        self.add_widget(root)

    def create_stat_card(self, title, value, accent):

        box = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(4))

        with box.canvas.before:
            Color(0.16, 0.17, 0.28, 1)
            bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[20])
            Color(*accent)
            border = Line(
                rounded_rectangle=(box.x, box.y, box.width, box.height, 20),
                width=1.2
            )

        def refresh(*args):
            bg.pos = box.pos
            bg.size = box.size
            border.rounded_rectangle = (box.x, box.y, box.width, box.height, 20)

        box.bind(pos=refresh, size=refresh)

        lbl_title = Label(text=title, font_size=dp(11), color=(0.8, 0.8, 0.9, 1))
        lbl_val = Label(text=value, font_size=dp(22), bold=True, color=accent)

        box.value_label = lbl_val
        box.add_widget(lbl_title)
        box.add_widget(lbl_val)

        return box

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

    def _update_bg(self, *args):
        self.bg.pos = self.children[0].pos
        self.bg.size = self.children[0].size

    def update_camera_card(self, *args):
        c = self.children[0].children[2]
        self.camera_bg.pos = c.pos
        self.camera_bg.size = c.size
        self.camera_border.rounded_rectangle = (c.x, c.y, c.width, c.height, 28)

    def update_status_card(self, *args):
        self.status_bg.pos = self.status_card.pos
        self.status_bg.size = self.status_card.size

    def _go_to(self, screen_name):
        self.manager.current = screen_name

    def update_status(self, status, ear, alerts):

        self.status_lbl.text = f"[b]{status}[/b]"
        self.ear_box.value_label.text = f"{ear:.3f}"
        self.alert_box.value_label.text = str(alerts)

        if status == "DROWSY":
            self.status_lbl.color = (1, 0.2, 0.3, 1)
        elif status == "AWAKE":
            self.status_lbl.color = (0.2, 1, 0.4, 1)
        else:
            self.status_lbl.color = (1, 0.8, 0.1, 1)

    def update_frame(self, frame):

        import cv2
        from kivy.graphics.texture import Texture

        if frame is None:
            return

        try:
            flipped = cv2.flip(frame, 0)
            rgb = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
            ht, wd = rgb.shape[:2]

            tex = Texture.create(size=(wd, ht), colorfmt='rgb')
            tex.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')

            self.cam_feed.texture = tex

        except Exception as err:
            print("Frame update error:", err)