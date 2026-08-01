from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.metrics import dp
from kivy.core.window import Window


class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):

        root = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(18))

        with root.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
            Color(0.6, 0.2, 1, 0.18)
            self.glow1 = Ellipse(pos=(-120, 500), size=(350, 350))
            Color(0.1, 0.7, 1, 0.15)
            self.glow2 = Ellipse(pos=(250, -100), size=(400, 400))

        root.bind(pos=self.update_bg, size=self.update_bg)

        header = BoxLayout(orientation='vertical', spacing=dp(5), size_hint=(1, 0.15))

        title = Label(
            text='[b]DRIVER MONITORING[/b]',
            markup=True,
            font_size=dp(34),
            color=(1, 1, 1, 1),
            bold=True
        )

        subtitle = Label(
            text='Real-Time Drowsiness Monitoring System',
            font_size=dp(15),
            color=(0.75, 0.8, 1, 1)
        )

        header.add_widget(title)
        header.add_widget(subtitle)

        card = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(22),
            size_hint=(1, 0.45)
        )

        with card.canvas.before:
            Color(0.12, 0.13, 0.22, 0.92)
            self.card_bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[30]
            )
            Color(0.5, 0.7, 1, 0.4)
            self.card_border = Line(
                rounded_rectangle=(card.x, card.y, card.width, card.height, 30),
                width=1.5
            )

        card.bind(pos=self.update_card, size=self.update_card)

        self.status_label = Label(
            text='[b]WAITING[/b]',
            markup=True,
            font_size=dp(38),
            color=(1, 0.8, 0.1, 1),
            bold=True,
            size_hint=(1, 0.3)
        )

        stats = GridLayout(cols=2, spacing=dp(15), size_hint=(1, 0.7))

        self.ear_box = self.create_stat_card("EAR VALUE", "0.000", (0.2, 0.85, 1, 1))
        self.alert_box = self.create_stat_card("ALERTS", "0", (1, 0.35, 0.45, 1))
        self.eye_box = self.create_stat_card("EYES CLOSED", "0.0 s", (1, 0.75, 0.2, 1))
        self.camera_box = self.create_stat_card("CAMERA", "ACTIVE", (0.2, 1, 0.5, 1))

        stats.add_widget(self.ear_box)
        stats.add_widget(self.alert_box)
        stats.add_widget(self.eye_box)
        stats.add_widget(self.camera_box)

        card.add_widget(self.status_label)
        card.add_widget(stats)

        self.start_btn = Button(
            text='START DETECTION',
            size_hint=(1, 0.12),
            font_size=dp(18),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )

        with self.start_btn.canvas.before:
            Color(0.8, 0.2, 1, 1)
            self.btn_bg = RoundedRectangle(
                pos=self.start_btn.pos,
                size=self.start_btn.size,
                radius=[22]
            )

        self.start_btn.bind(pos=self.update_btn, size=self.update_btn)
        self.start_btn.bind(on_press=self._on_start)

        nav = GridLayout(cols=3, spacing=dp(12), size_hint=(1, 0.11))

        btn_dash = self.create_nav_button("Dashboard", (0.45, 0.2, 1, 1))
        btn_graph = self.create_nav_button("EAR Graph", (0.1, 0.7, 1, 1))
        btn_hist = self.create_nav_button("History", (1, 0.4, 0.5, 1))

        btn_dash.bind(on_press=lambda x: self._go_to('dashboard'))
        btn_graph.bind(on_press=lambda x: self._go_to('graph'))
        btn_hist.bind(on_press=lambda x: self._go_to('history'))

        nav.add_widget(btn_dash)
        nav.add_widget(btn_graph)
        nav.add_widget(btn_hist)

        footer = Label(
            text='Drive Safe • Smart Detection Enabled',
            font_size=dp(12),
            color=(0.7, 0.7, 0.8, 1),
            size_hint=(1, 0.05)
        )

        root.add_widget(header)
        root.add_widget(card)
        root.add_widget(self.start_btn)
        root.add_widget(nav)
        root.add_widget(footer)

        self.add_widget(root)

    def create_stat_card(self, title, value, accent):

        box = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(5))

        with box.canvas.before:
            Color(0.16, 0.18, 0.30, 0.95)
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
        lbl_val = Label(text=value, font_size=dp(24), bold=True, color=accent)

        box.value_label = lbl_val
        box.add_widget(lbl_title)
        box.add_widget(lbl_val)

        return box

    def create_nav_button(self, text, color_theme):

        btn = Button(
            text=text,
            font_size=dp(14),
            bold=True,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
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

    def update_card(self, *args):
        c = self.children[0].children[3]
        self.card_bg.pos = c.pos
        self.card_bg.size = c.size
        self.card_border.rounded_rectangle = (c.x, c.y, c.width, c.height, 30)

    def update_btn(self, *args):
        self.btn_bg.pos = self.start_btn.pos
        self.btn_bg.size = self.start_btn.size

    def _go_to(self, screen):
        self.manager.current = screen

    def _on_start(self, instance):
        from kivy.app import App
        App.get_running_app().toggle_detection()

    def update_status(self, status, ear, alerts=0):

        self.status_label.text = f"[b]{status}[/b]"
        self.ear_box.value_label.text = f"{ear:.3f}"
        self.alert_box.value_label.text = str(alerts)

        if status == "DROWSY":
            self.status_label.color = (1, 0.2, 0.3, 1)
        elif status == "AWAKE":
            self.status_label.color = (0.2, 1, 0.5, 1)
        else:
            self.status_label.color = (1, 0.8, 0.1, 1)

    def set_running(self, running):
        if running:
            self.start_btn.text = "STOP DETECTION"
            self.btn_bg.radius = [22]
        else:
            self.start_btn.text = "START DETECTION"
            self.btn_bg.radius = [22]