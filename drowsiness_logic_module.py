import time
import numpy as np

class DrowsinessDetector:
    """
    Implements EAR-based drowsiness detection.
    """

    def __init__(self, ear_threshold=0.25, time_threshold=2):
        self.ear_threshold = ear_threshold
        self.time_threshold = time_threshold

        self.start_time = None
        self.is_drowsy = False
        self.current_ear = 0
        self.history = []

    def calculate_distance(self, p1, p2):
        """Calculate distance between two points."""
        return np.linalg.norm([p1.x - p2.x, p1.y - p2.y])

    def calculate_ear(self, eye):
        """Compute EAR."""
        try:
            p1,p2,p3,p4,p5,p6 = eye

            v1 = self.calculate_distance(p2,p6)
            v2 = self.calculate_distance(p3,p5)
            h  = self.calculate_distance(p1,p4)

            if h == 0:
                return 0

            return (v1 + v2) / (2*h)
        except:
            return 0

    def average_ear(self, left, right):
        """Average EAR."""
        left_val = self.calculate_ear(left)
        right_val = self.calculate_ear(right)

        self.current_ear = (left_val + right_val)/2
        self.history.append(self.current_ear)

        return self.current_ear

    def check_drowsiness(self, ear):
        """Check drowsiness."""
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
        """Reset state."""
        self.start_time = None
        self.is_drowsy = False

    def get_average_history(self):
        """Return average EAR history."""
        if len(self.history) == 0:
            return 0
        return sum(self.history)/len(self.history)
