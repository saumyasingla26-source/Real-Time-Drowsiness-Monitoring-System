import cv2

class CameraModule:
    """
    Handles all camera-related operations such as:
    initialization, frame capture, processing, and release.
    """

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.frame_count = 0

    def start_camera(self):
        """Start the camera."""
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise Exception("Camera not accessible")

        self.running = True
        print("Camera started")

    def read_frame(self):
        """Read a frame from camera."""
        if not self.running:
            return None

        ret, frame = self.cap.read()

        if not ret:
            print("Frame capture failed")
            return None

        self.frame_count += 1
        return frame

    def resize_frame(self, frame, width=640, height=480):
        """Resize frame for processing."""
        try:
            return cv2.resize(frame, (width, height))
        except:
            return frame

    def convert_to_gray(self, frame):
        """Convert frame to grayscale."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def flip_frame(self, frame):
        """Flip frame horizontally."""
        return cv2.flip(frame, 1)

    def draw_text(self, frame, text, position=(20, 40), color=(0,255,0)):
        """Draw text on frame."""
        cv2.putText(frame, text, position,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    def draw_rectangle(self, frame, x, y, w, h):
        """Draw rectangle (optional use)."""
        cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

    def display_frame(self, frame, window_name="Drowsiness Detection"):
        """Display frame."""
        cv2.imshow(window_name, frame)

    def get_key(self):
        """Get key press."""
        return cv2.waitKey(1) & 0xFF

    def is_running(self):
        """Check if camera is active."""
        return self.running

    def get_frame_count(self):
        """Return number of frames processed."""
        return self.frame_count

    def stop_camera(self):
        """Release camera."""
        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()
        self.running = False
        print("Camera stopped")