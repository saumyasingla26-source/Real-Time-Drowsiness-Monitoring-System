import cv2
import mediapipe as mp


class EyeDetection:

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # 6 points per eye, order matters for EAR calc
        self.left_eye_indices  = [33, 160, 158, 133, 153, 144]
        self.right_eye_indices = [362, 385, 387, 263, 373, 380]

    def convert_to_rgb(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def get_landmarks(self, frame):
        rgb_frame = self.convert_to_rgb(frame)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0].landmark
        return None

    def get_eye_points(self, landmarks):
        if landmarks is None:
            return None, None
        left_eye  = [landmarks[i] for i in self.left_eye_indices]
        right_eye = [landmarks[i] for i in self.right_eye_indices]
        return left_eye, right_eye

    def draw_eye_points(self, frame, eye_points):
        if eye_points is None:
            return frame
        height, width = frame.shape[:2]
        for point in eye_points:
            x = int(point.x * width)
            y = int(point.y * height)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        return frame

    def draw_bounding_box(self, frame, landmarks):
        if landmarks is None:
            return frame
        h, w = frame.shape[:2]
        x_coords = [int(p.x * w) for p in landmarks]
        y_coords = [int(p.y * h) for p in landmarks]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        return frame

    def process(self, frame):
        landmarks = self.get_landmarks(frame)
        if landmarks is None:
            return None, None, None
        left_eye, right_eye = self.get_eye_points(landmarks)
        return landmarks, left_eye, right_eye

    def release(self):
        self.face_mesh.close()
