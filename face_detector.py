import os
import time  # Used to generate increasing timestamps required by VIDEO mode

import cv2
import mediapipe as mp

# As of mediapipe 1.0, the old "mp.solutions" API was removed entirely.
# Face detection now lives in the newer "Tasks" API instead, which needs
# these shortcuts and a separately-downloaded .task model file.
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Default location of the model file, relative to this file (not to wherever
# the script happens to be run from).
RUTA_MODELO_POR_DEFECTO = os.path.join(os.path.dirname(__file__), "assets", "face_landmarker.task")


class FaceDetector:
    """
    Wraps Mediapipe's Face Landmarker (the current Tasks API): takes a video
    frame and returns the detected facial landmarks, without the rest of the
    program needing to know how Mediapipe works internally.
    """

    def __init__(self, ruta_modelo=RUTA_MODELO_POR_DEFECTO, max_caras=1,
                 confianza_deteccion=0.5, confianza_seguimiento=0.5):
        # Constructor: stores the configuration and creates the Mediapipe object.
        # Unlike CameraManager, we create the model right away here, since
        # loading it doesn't touch external hardware (like the camera), it
        # just loads the model file into memory.

        self.ruta_modelo = ruta_modelo                     # Path to the .task model file
        self.max_caras = max_caras                         # Maximum number of faces to detect at once
        self.confianza_deteccion = confianza_deteccion      # How confident it must be to "see" a face
        self.confianza_seguimiento = confianza_seguimiento  # How confident it must be to keep tracking it

        if not os.path.exists(self.ruta_modelo):
            # Without this check, Mediapipe raises a much harder-to-read internal
            # error if the model file is missing or the path is wrong.
            raise FileNotFoundError(f"Model file not found at: {self.ruta_modelo}")

        opciones = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.ruta_modelo),
            running_mode=VisionRunningMode.VIDEO,  # Synchronous, frame-by-frame mode (fits our detect() design)
            num_faces=self.max_caras,
            min_face_detection_confidence=self.confianza_deteccion,
            min_tracking_confidence=self.confianza_seguimiento,
        )

        self.landmarker = FaceLandmarker.create_from_options(opciones)  # The actual model

        self._inicio = time.time()  # Reference point to build increasing timestamps (VIDEO mode requires them)

    def detect(self, frame):
        """
        Processes one video frame and returns the detected face's landmarks,
        or None if no face was found.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR, Mediapipe expects RGB
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)  # Mediapipe's own image wrapper

        timestamp_ms = int((time.time() - self._inicio) * 1000)  # Must keep increasing between calls
        resultado = self.landmarker.detect_for_video(mp_image, timestamp_ms)  # Runs the model on this frame

        if not resultado.face_landmarks:
            return None  # No face detected in this frame

        return resultado.face_landmarks[0]  # max_caras=1, so just the first (and only) face

    def draw_landmarks(self, frame, landmarks):
        """
        Draws the full face mesh (all detected points, connected by lines)
        on top of a copy of the frame. The original frame is not modified.
        This is for debugging/visualization, not for the actual AR filters.
        """
        frame_dibujado = frame.copy()  # Keep the original frame untouched

        mp.tasks.vision.drawing_utils.draw_landmarks(
            image=frame_dibujado,
            landmark_list=landmarks,
            connections=mp.tasks.vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.tasks.vision.drawing_styles.get_default_face_mesh_tesselation_style(),
        )

        return frame_dibujado

    def get_landmark_coordinates(self, frame, landmark):
        """
        Converts a single landmark's normalized coordinates (0 to 1, relative
        to the image size) into real pixel coordinates for the given frame.
        Returns an (x_pixel, y_pixel) tuple.
        """
        alto, ancho = frame.shape[:2]  # frame.shape = (height, width, channels)

        x_pixel = int(landmark.x * ancho)
        y_pixel = int(landmark.y * alto)

        return (x_pixel, y_pixel)

    def get_landmarks_coordinates(self, frame, landmarks):
        """
        Same as get_landmark_coordinates, but for several landmarks at once.
        Returns a list of (x_pixel, y_pixel) tuples, one per landmark, in
        the same order they were given.
        """
        return [self.get_landmark_coordinates(frame, landmark) for landmark in landmarks]

    def close(self):
        """
        Releases the Face Landmarker's internal resources.
        Should be called when the program ends, similar to CameraManager.release().
        """
        self.landmarker.close()
