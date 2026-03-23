from camera_module import CameraModule
from eye_detection_module import EyeDetection
from drowsiness_logic_module import DrowsinessDetector
from alarm_module import AlarmSystem
from database_module import DatabaseManager

# Initialize modules
camera = CameraModule()
eye = EyeDetection()
logic = DrowsinessDetector()
alarm = AlarmSystem()
db = DatabaseManager()

# Start camera
camera.start_camera()

print("System Started... Press ESC to exit")

# Main loop
while camera.is_running():
    try:
        frame = camera.read_frame()

        # If frame not captured, skip instead of closing
        if frame is None:
            continue

        # Preprocessing
        frame = camera.resize_frame(frame)
        frame = camera.flip_frame(frame)

        # Eye detection
        landmarks, left_eye, right_eye = eye.process(frame)

        # If detection fails, continue safely
        if left_eye is None or right_eye is None:
            camera.draw_text(frame, "Face not detected", (20, 40))
            camera.display_frame(frame)
            continue

        # Calculate EAR
        ear = logic.average_ear(left_eye, right_eye)
        drowsy = logic.check_drowsiness(ear)

        status = "DROWSY" if drowsy else "AWAKE"

        # Display info
        camera.draw_text(frame, f"Status: {status}", (20, 40))
        camera.draw_text(frame, f"EAR: {round(ear, 3)}", (20, 80))

        # Draw eye points
        eye.draw_eye_points(frame, left_eye)
        eye.draw_eye_points(frame, right_eye)

        # Alarm trigger
        if drowsy:
            alarm.ring_alarm()

            # Safe database insert
            try:
                db.insert_record(ear, status)
            except Exception as e:
                print("Database error:", e)

        # Show frame
        camera.display_frame(frame)

        # Exit key
        key = camera.get_key()
        if key == 27 or key == ord('q'):
            print("Exiting...")
            break

    except Exception as e:
        print("Runtime error:", e)
        continue

# Cleanup
camera.stop_camera()
db.close()

print("System Stopped Successfully")