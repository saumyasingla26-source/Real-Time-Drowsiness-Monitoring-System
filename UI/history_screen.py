from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
from kivy.metrics import dp


class HistoryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):

        root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(15))

        with root.canvas.before:
            Color(0.05, 0.05, 0.09, 1)
            self.bg = RoundedRectangle(pos=root.pos, size=root.size)
            Color(0.7, 0.2, 1, 0.15)
            self.glow1 = Ellipse(pos=(-100, 450), size=(320, 320))
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

        title = Label(text='[b]DETECTION HISTORY[/b]', markup=True, font_size=dp(24), color=(1, 1, 1, 1))

        top_bar.add_widget(home_btn)
        top_bar.add_widget(title)

        filter_row = GridLayout(cols=3, spacing=dp(12), size_hint=(1, 0.10))

        btn_today = self.create_filter_button("TODAY", (0.1, 0.7, 1, 1))
        btn_yesterday = self.create_filter_button("YESTERDAY", (0.55, 0.25, 1, 1))
        btn_days = self.create_filter_button("5 DAYS", (1, 0.35, 0.45, 1))

        btn_today.bind(on_press=lambda x: self.load_history("today"))
        btn_yesterday.bind(on_press=lambda x: self.load_history("yesterday"))
        btn_days.bind(on_press=lambda x: self.load_history("5days"))

        filter_row.add_widget(btn_today)
        filter_row.add_widget(btn_yesterday)
        filter_row.add_widget(btn_days)

        history_card = BoxLayout(orientation='vertical', padding=dp(12), size_hint=(1, 0.78))

        with history_card.canvas.before:
            Color(0.13, 0.14, 0.24, 0.93)
            self.history_bg = RoundedRectangle(pos=history_card.pos, size=history_card.size, radius=[28])
            Color(0.1, 0.8, 1, 0.4)
            self.history_border = Line(
                rounded_rectangle=(history_card.x, history_card.y, history_card.width, history_card.height, 28),
                width=1.5
            )

        history_card.bind(pos=self.update_history_card, size=self.update_history_card)

        scroll = ScrollView(bar_width=dp(4))

        self.history_layout = GridLayout(
            cols=1, spacing=dp(12), padding=dp(10), size_hint_y=None
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        scroll.add_widget(self.history_layout)
        history_card.add_widget(scroll)

        root.add_widget(top_bar)
        root.add_widget(filter_row)
        root.add_widget(history_card)

        self.add_widget(root)

    def create_filter_button(self, text, color_theme):

        btn = Button(
            text=text, font_size=dp(13), bold=True,
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

    def update_history_card(self, *args):
        c = self.children[0].children[0]
        self.history_bg.pos = c.pos
        self.history_bg.size = c.size
        self.history_border.rounded_rectangle = (c.x, c.y, c.width, c.height, 28)

    def go_home(self):
        self.manager.current = 'home'

    def load_history(self, mode="today"):

        self.history_layout.clear_widgets()

        try:
            from kivy.app import App
            app = App.get_running_app()

            if not app.db:
                return

            rows = app.db.get_filtered_records(mode)

            if not rows:
                empty = Label(
                    text="No Records Found",
                    size_hint_y=None, height=dp(60),
                    font_size=dp(18), color=(1, 1, 1, 1)
                )
                self.history_layout.add_widget(empty)
                return

            for row in rows:
                date = row[2]
                time = row[3]
                ear = row[4]
                status = row[5]

                card = BoxLayout(
                    orientation='vertical', padding=dp(15),
                    spacing=dp(8), size_hint_y=None, height=dp(110)
                )

                accent = (1, 0.3, 0.4, 1) if status == "DROWSY" else (0.2, 1, 0.5, 1)

                with card.canvas.before:
                    Color(0.16, 0.17, 0.28, 1)
                    bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[24])
                    Color(*accent)
                    border = Line(
                        rounded_rectangle=(card.x, card.y, card.width, card.height, 24),
                        width=1.4
                    )

                def refresh(inst, val, c=card, b=bg, bd=border):
                    b.pos = c.pos
                    b.size = c.size
                    bd.rounded_rectangle = (c.x, c.y, c.width, c.height, 24)

                card.bind(pos=refresh, size=refresh)

                top = BoxLayout(orientation='horizontal')

                lbl_date = Label(text=f"[b]{date}[/b]", markup=True, halign='left', color=(1, 1, 1, 1), font_size=dp(14))
                lbl_status = Label(text=f"[b]{status}[/b]", markup=True, halign='right', color=accent, font_size=dp(14))

                top.add_widget(lbl_date)
                top.add_widget(lbl_status)

                details = Label(
                    text=f"Time : {time}\nEAR Value : {round(ear, 3)}",
                    color=(0.82, 0.82, 0.92, 1), font_size=dp(13)
                )

                card.add_widget(top)
                card.add_widget(details)

                self.history_layout.add_widget(card)

        except Exception as err:
            print("History load error:", err)

    def on_enter(self, *args):
        self.load_history("today")