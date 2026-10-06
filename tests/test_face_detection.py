import os
import sys

# Allow running this script from inside tests/, while still importing the
# project's own modules (camara_manager, face_detector, etc.) from the
# parent folder.
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ_PROYECTO)

import cv2
from camara_manager import CameraManager
from face_detector import FaceDetector

# Quick integration test for CameraManager + FaceDetector.
# Not part of the final app (main.py replaces this) - just a way to
# visually confirm both classes work together.


def main():
    indice_camara = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print(f"Using camera index {indice_camara}")

    camara = CameraManager(indice_camara=indice_camara)
    camara.start()

    detector = FaceDetector()

    print("Press 'q' in the video window to quit.")

    while True:
        frame = camara.read_frame()
        if frame is None:
            print("Could not read frame from camera.")
            break

        landmarks = detector.detect(frame)

        if landmarks is not None:
            frame = detector.draw_landmarks(frame, landmarks)
            texto = "Face detected"
            color = (0, 255, 0)
        else:
            texto = "No face detected"
            color = (0, 0, 255)

        cv2.putText(frame, f"Camera {indice_camara} - {texto}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Test - CameraManager + FaceDetector", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
