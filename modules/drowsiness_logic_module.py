import time
import numpy as np


EAR_THRESHOLD = 0.25
TIME_THRESHOLD = 2  # seconds eyes must stay closed to count as drowsy


class DrowsinessDetector:

    def __init__(self, ear_threshold=EAR_THRESHOLD, time_threshold=TIME_THRESHOLD):
        self.ear_threshold = ear_threshold
        self.time_threshold = time_threshold
        self.start_time = None
        self.is_drowsy = False
        self.current_ear = 0
        self.history = []

    def calculate_distance(self, p1, p2):
        return np.linalg.norm([p1.x - p2.x, p1.y - p2.y])

    def calculate_ear(self, eye):
        try:
            p1, p2, p3, p4, p5, p6 = eye
            v1 = self.calculate_distance(p2, p6)
            v2 = self.calculate_distance(p3, p5)
            h = self.calculate_distance(p1, p4)
            if not h:
                return 0
            return (v1 + v2) / (2 * h)
        except Exception:
            return 0

    def average_ear(self, left, right):
        left_val = self.calculate_ear(left)
        right_val = self.calculate_ear(right)
        self.current_ear = (left_val + right_val) / 2
        self.history.append(self.current_ear)
        return self.current_ear

    def check_drowsiness(self, ear):
        if ear < self.ear_threshold:
            if self.start_time is None:
                self.start_time = time.time()
            else:
                duration = time.time() - self.start_time
                if duration >= self.time_threshold:
                    self.is_drowsy = True
        else:
            self.reset()
        return self.is_drowsy

    def reset(self):
        self.start_time = None
        self.is_drowsy = False

    def get_average_history(self):
        if not self.history:
            return 0
        return sum(self.history) / len(self.history)
