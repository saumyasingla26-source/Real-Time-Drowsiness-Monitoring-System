import winsound
import threading

class AlarmSystem:
    def _init_(self):
        # MUST be defined here
        self.is_on = False

    def _beep(self):
        """Internal function to play sound"""
        try:
            for _ in range(3):
                winsound.Beep(1000, 500)
        except:
            print("Sound error")

    def ring_alarm(self):
        """Trigger alarm safely"""
        try:
            if not hasattr(self, 'is_on'):
                self.is_on = False   # safety fix

            if not self.is_on:
                self.is_on = True
                print("🚨 DROWSINESS ALERT!")

                # run in background thread
                t = threading.Thread(target=self._beep)
                t.daemon = True
                t.start()

                self.is_on = False

        except Exception as e:
            print("Alarm error:", e)