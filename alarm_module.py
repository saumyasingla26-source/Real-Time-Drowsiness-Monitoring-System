from playsound import playsound

class AlarmSystem:
    """
    Handles alarm triggering and control.
    """

    def __init__(self, file="alarm.mp3"):
        self.file = file
        self.active = False

    def play(self):
        try:
            self.active = True
            playsound(self.file)
        except:
            print("Alarm failed")
        finally:
            self.active = False

    def trigger(self):
        if not self.active:
            print("ALERT: Drowsiness detected")
            self.play()
