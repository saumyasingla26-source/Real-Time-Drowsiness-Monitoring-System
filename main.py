from camera_module import CameraModule
from eye_detection_module import EyeDetection
from drowsiness_logic_module import DrowsinessDetector
from alarm_module import AlarmSystem
from database_module import DatabaseManager

camera = CameraModule()
eye = EyeDetection()
logic = DrowsinessDetector()
alarm = AlarmSystem()
db = DatabaseManager()

camera.start_camera()

while camera.is_running():
    frame = camera.read_frame()
    if frame is None:
        break

    frame = camera.resize_frame(frame)
    frame = camera.flip_frame(frame)

    landmarks, left_eye, right_eye = eye.process(frame)

    if left_eye and right_eye:
        ear = logic.average_ear(left_eye, right_eye)
        drowsy = logic.check_drowsiness(ear)

        status = "DROWSY" if drowsy else "AWAKE"

        camera.draw_text(frame, f"Status: {status}")
        camera.draw_text(frame, f"EAR: {round(ear,3)}", (20,80))

        eye.draw_eye_points(frame, left_eye)
        eye.draw_eye_points(frame, right_eye)

        if drowsy:
            alarm.trigger()
            db.insert_record(ear, status)

    camera.display_frame(frame)

    if camera.get_key() == 27:
        break

camera.stop_camera()
db.close()