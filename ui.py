from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2

from eye_detection_module import EyeDetection
from drowsiness_logic_module import DrowsinessDetector
from alarm_module import AlarmSystem


KV = '''
MDBoxLayout:
    orientation: "horizontal"

    # 🔹 SIDEBAR
    MDBoxLayout:
        orientation: "vertical"
        size_hint_x: 0.22
        padding: 10
        spacing: 20
        md_bg_color: 0.12, 0.12, 0.12, 1

        MDLabel:
            text: "🚗 DMS"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 1,1,1,1
            font_style: "H5"

        MDRaisedButton:
            text: "Start"
            md_bg_color: 0, 0.7, 0.3, 1
            on_release: app.start_camera()

        MDRaisedButton:
            text: "Stop"
            md_bg_color: 0.8, 0, 0, 1
            on_release: app.stop_app()

    # 🔹 MAIN AREA
    MDBoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 10

        MDTopAppBar:
            title: "Driver Monitoring Dashboard"
            md_bg_color: 0.1, 0.5, 0.8, 1

        # CAMERA
        MDCard:
            size_hint_y: 0.6
            radius: [15]
            elevation: 8

            Image:
                id: cam_feed

        # STATUS ROW
        MDGridLayout:
            cols: 3
            spacing: 10
            size_hint_y: 0.4

            MDCard:
                radius: [15]
                elevation: 6

                MDLabel:
                    id: status
                    text: "Status: Waiting..."
                    halign: "center"
                    font_style: "H6"

            MDCard:
                radius: [15]
                elevation: 6

                MDLabel:
                    id: ear
                    text: "EAR: 0.0"
                    halign: "center"

            MDCard:
                radius: [15]
                elevation: 6

                MDLabel:
                    id: alerts
                    text: "Alerts: 0"
                    halign: "center"
'''


class DashboardApp(MDApp):

    def build(self):
        self.eye = EyeDetection()
        self.logic = DrowsinessDetector()
        self.alarm = AlarmSystem()

        self.capture = None
        self.running = False
        self.alert_count = 0

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        return Builder.load_string(KV)

    def start_camera(self):
        if not self.running:
            self.capture = cv2.VideoCapture(0)
            self.running = True
            Clock.schedule_interval(self.update, 1/30)

    def update(self, dt):
        if not self.running or self.capture is None:
            return

        ret, frame = self.capture.read()
        if not ret:
            self.root.ids.status.text = "Camera Error"
            return

        # Flip + convert
        frame = cv2.flip(frame, 0)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            landmarks, left_eye, right_eye = self.eye.process(frame)

            if left_eye and right_eye:
                ear = self.logic.average_ear(left_eye, right_eye)
                drowsy = self.logic.check_drowsiness(ear)

                self.root.ids.ear.text = f"EAR: {round(ear,3)}"

                if drowsy:
                    self.root.ids.status.text = "🚨 DROWSY"
                    self.root.ids.status.text_color = (1, 0, 0, 1)

                    self.alert_count += 1
                    self.root.ids.alerts.text = f"Alerts: {self.alert_count}"

                    self.alarm.ring_alarm()
                else:
                    self.root.ids.status.text = "😊 AWAKE"
                    self.root.ids.status.text_color = (0, 1, 0, 1)

            else:
                self.root.ids.status.text = "No Face Detected"
                self.root.ids.status.text_color = (1, 0.5, 0, 1)

        except Exception as e:
            print("Error:", e)
            self.root.ids.status.text = "Detection Error"

        # Display frame
        texture = Texture.create(size=(rgb.shape[1], rgb.shape[0]), colorfmt='rgb')
        texture.blit_buffer(rgb.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.root.ids.cam_feed.texture = texture

    def stop_app(self):
        self.running = False
        if self.capture:
            self.capture.release()
        self.stop()


if __name__ == "__main__":
    DashboardApp().run()