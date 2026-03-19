from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
import os

class MainLayout(BoxLayout):
    def start(self):
        os.system("python main.py")

    def exit(self):
        exit()

class App(MDApp):
    def build(self):
        return MainLayout()

App().run()
