import sys
import os
import traceback
import threading


def _write_crash(exc):
    try:
        from kivy.app import App
        log_dir = App.get_running_app().user_data_dir
    except Exception:
        log_dir = os.getcwd()

    path = os.path.join(log_dir, "crash_log.txt")
    with open(path, "a") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(traceback.format_exc())
    print("Crash log written to:", path)


def _excepthook(exc_type, exc_value, exc_tb):
    _write_crash(exc_value)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.uix.label import Label


class DrowsinessApp(App):

    def build(self):

        Window.clearcolor = (0.05, 0.05, 0.12, 1)

        try:
            from UI.home_screen import HomeScreen
            from UI.dashboard_screen import DashboardScreen
            from UI.graph_screen import GraphScreen
            from UI.history_screen import HistoryScreen
        except Exception as err:
            _write_crash(err)
            return Label(text=f"UI load error:\n{err}", color=(1, 0, 0, 1))

        self.sm = ScreenManager(transition=FadeTransition())

        self.home_screen = HomeScreen(name='home')
        self.dashboard_screen = DashboardScreen(name='dashboard')
        self.graph_screen = GraphScreen(name='graph')
        self.history_screen = HistoryScreen(name='history')

        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.dashboard_screen)
        self.sm.add_widget(self.graph_screen)
        self.sm.add_widget(self.history_screen)

        self.camera = None
        self.eye = None
        self.detector = None
        self.alarm = None
        self.db = None

        self.is_running = False
        self._cam_thread = None
        self.total_alerts = 0
        self._graph_counter = 0
        self._modules_ready = False

        return self.sm

    def on_start(self):
        Clock.schedule_once(self._load_modules, 0.5)

    def _load_modules(self, dt):

        try:
            from modules.camera_module import CameraModule
            from modules.eye_detection_module import EyeDetection
            from modules.drowsiness_logic_module import DrowsinessDetector
            from modules.alarm_module import AlarmSystem
            from modules.database_module import DatabaseManager

            self.camera = CameraModule()
            self.detector = DrowsinessDetector()
            self.alarm = AlarmSystem()

            try:
                self.eye = EyeDetection()
            except Exception as err:
                _write_crash(err)
                self._update_ui_status("MediaPipe error", 0, 0)
                return

            try:
                self.db = DatabaseManager()
            except Exception as err:
                print("DB init error:", err)
                self.db = None

            self._modules_ready = True
            print("All modules loaded successfully")
            self._update_ui_status("Ready", 0, 0)

        except Exception as err:
            _write_crash(err)
            self._update_ui_status(f"Load error: {err}", 0, 0)

    def toggle_detection(self):

        if not self._modules_ready:
            print("Modules not ready yet")
            self._update_ui_status("Loading...", 0, 0)
            return

        if self.is_running:
            self._stop_detection()
        else:
            self._start_detection()

    def _start_detection(self):

        try:
            self.camera.start_camera()
            self.is_running = True
            self._graph_counter = 0
            self.home_screen.set_running(True)

            self._cam_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._cam_thread.start()
            print("Detection started")

        except Exception as err:
            _write_crash(err)
            self._update_ui_status("Camera Error", 0, self.total_alerts)

    def _stop_detection(self):

        self.is_running = False

        if self.camera:
            self.camera.running = False
            try:
                self.camera.stop_camera()
            except Exception:
                pass

        if self.db:
            try:
                avg = self.detector.get_average_history()
                self.db.end_session(avg, self.total_alerts)
            except Exception as err:
                print("DB session end error:", err)

        self.home_screen.set_running(False)
        self._update_ui_status("Stopped", 0, self.total_alerts)
        print("Detection stopped")

    def _detection_loop(self):

        while self.is_running:

            try:
                frame = self.camera.read_frame()
                if frame is None:
                    continue

                frame = self.camera.resize_frame(frame)
                frame = self.camera.flip_frame(frame)

                landmarks, left_eye, right_eye = self.eye.process(frame)

                if left_eye is None or right_eye is None:
                    self.camera.draw_text(frame, "No Face", (20, 40), (0, 165, 255))
                    self._push_frame(frame)
                    self._update_ui_status("No Face", 0, self.total_alerts)
                    continue

                ear = self.detector.average_ear(left_eye, right_eye)
                drowsy = self.detector.check_drowsiness(ear)

                if drowsy:
                    status = "DROWSY"
                    col = (0, 0, 255)
                    self.total_alerts += 1
                    self.alarm.ring_alarm()
                else:
                    status = "AWAKE"
                    col = (0, 255, 0)

                if self.db:
                    try:
                        self.db.insert_record(ear, status)
                        print("Inserted:", ear, status)
                    except Exception as db_err:
                        print("DB insert error:", db_err)

                self.camera.draw_text(frame, f"Status: {status}", (20, 40), col)
                self.camera.draw_text(frame, f"EAR: {round(ear, 3)}", (20, 80), (200, 200, 200))

                self.eye.draw_eye_points(frame, left_eye)
                self.eye.draw_eye_points(frame, right_eye)

                self._push_frame(frame)
                self._update_ui_status(status, ear, self.total_alerts)

                self._graph_counter += 1
                if self._graph_counter % 30 == 0:
                    self._update_graph(self.detector.history[:])

            except Exception as err:
                print("Loop error:", err)
                continue

    @mainthread
    def _push_frame(self, frame):
        self.dashboard_screen.update_frame(frame)

    @mainthread
    def _update_ui_status(self, status, ear, alerts):
        self.home_screen.update_status(status, ear, alerts)
        self.dashboard_screen.update_status(status, ear, alerts)

    @mainthread
    def _update_graph(self, history):
        self.graph_screen.update_graph(history)

    def on_stop(self):

        self._stop_detection()

        try:
            if self.eye:
                self.eye.release()
        except Exception:
            pass

        if self.db:
            try:
                self.db.close()
            except Exception:
                pass

        print("App stopped cleanly")


if __name__ == '__main__':
    try:
        DrowsinessApp().run()
    except Exception as err:
        _write_crash(err)
        raise