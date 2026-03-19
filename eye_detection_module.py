import cv2
import mediapipe as mp

class EyeDetection:
    """
    Detects face landmarks and extracts eye coordinates.
    """

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

        self.left_eye_indices = [33,160,158,133,153,144]
        self.right_eye_indices = [362,385,387,263,373,380]

    def convert_to_rgb(self, frame):
        """Convert BGR to RGB."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def detect_face(self, frame):
        """Detect face landmarks."""
        rgb = self.convert_to_rgb(frame)
        result = self.face_mesh.process(rgb)

        if result.multi_face_landmarks:
            return result.multi_face_landmarks[0].landmark

        return None

    def extract_eye_points(self, landmarks):
        """Extract eye landmarks."""
        if landmarks is None:
            return None, None

        left_eye = [landmarks[i] for i in self.left_eye_indices]
        right_eye = [landmarks[i] for i in self.right_eye_indices]

        return left_eye, right_eye

    def draw_eye_points(self, frame, eye_points):
        """Draw eye landmarks."""
        if eye_points is None:
            return frame

        h, w, _ = frame.shape

        for p in eye_points:
            x, y = int(p.x*w), int(p.y*h)
            cv2.circle(frame, (x,y), 2, (0,255,0), -1)

        return frame

    def process(self, frame):
        """Complete pipeline."""
        landmarks = self.detect_face(frame)
        left_eye, right_eye = self.extract_eye_points(landmarks)

        return landmarks, left_eye, right_eye