import cv2
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture


class CamApp(App):
    def build(self):
        self.img = Image()

        # Try multiple camera indexes
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(1)

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        return self.img

    def update(self, dt):
        if not self.capture:
            return

        ret, frame = self.capture.read()

        if not ret:
            print("Frame not coming")
            return

        # Convert properly
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 0)

        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        self.img.texture = texture


if __name__ == "__main__":
    CamApp().run()