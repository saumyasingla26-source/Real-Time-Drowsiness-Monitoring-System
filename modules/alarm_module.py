import threading
import os


class AlarmSystem:

    def __init__(self):
        self.is_on = False
        self._lock = threading.Lock()
        self._sound_path = None
        self._prepare_sound()

    def _get_writable_dir(self):
        try:
            from kivy.app import App
            running = App.get_running_app()
            if running:
                return running.user_data_dir
        except Exception:
            pass
        return os.getcwd()

    def _generate_wav(self, path):
        import wave
        import struct
        import math

        sr = 44100
        freq = 1000
        dur = 1
        total = sr * dur
        amp = 32767

        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for i in range(total):
                val = int(amp * math.sin(2 * math.pi * freq * i / sr))
                wf.writeframes(struct.pack('<h', val))

        print("WAV file saved at:", path)

    def _prepare_sound(self):
        try:
            mp3 = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets", "alarm.mp3"
            )
            if os.path.exists(mp3):
                self._sound_path = mp3
                print("Using bundled mp3")
                return

            wav = os.path.join(self._get_writable_dir(), "alarm_beep.wav")
            if not os.path.exists(wav):
                self._generate_wav(wav)
            self._sound_path = wav
            print("Using generated wav at", wav)

        except Exception as err:
            print("Sound prepare failed:", err)
            self._sound_path = None

    def _play(self):
        did_play = False

        if self._sound_path and os.path.exists(self._sound_path):
            try:
                from kivy.core.audio import SoundLoader
                snd = SoundLoader.load(self._sound_path)
                if snd:
                    snd.play()
                    did_play = True
                    print("Played via SoundLoader")
            except Exception as err:
                print("SoundLoader failed:", err)

        if not did_play:
            try:
                from plyer import vibrator
                vibrator.vibrate(1)
                did_play = True
                print("Vibrated via plyer")
            except Exception:
                pass

        if not did_play:
            print("DROWSINESS ALERT - no audio")

        with self._lock:
            self.is_on = False

    def ring_alarm(self):
        with self._lock:
            if self.is_on:
                return
            self.is_on = True

        print("DROWSINESS ALERT!")
        t = threading.Thread(target=self._play, daemon=True)
        t.start()