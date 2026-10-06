import cv2  # OpenCV: camera access and video processing


class CameraManager:
    """
    Manages the webcam: opening it, reading video frames, and releasing it.
    Isolates the rest of the program from OpenCV's internal details.
    """

    def __init__(self, indice_camara=0, ancho=640, alto=480):
        # Constructor: stores the configuration. The camera is not opened yet,
        # that happens in start().

        self.indice_camara = indice_camara  # 0 = default built-in camera
        self.ancho = ancho                  # Desired horizontal resolution
        self.alto = alto                    # Desired vertical resolution

        self.cap = None  # cv2.VideoCapture object; created in start()

    def start(self):
        """
        Opens the camera and applies the configured resolution.
        Must be called before using read_frame().
        """
        self.cap = cv2.VideoCapture(self.indice_camara)  # Opens the connection to the camera

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)   # Requests the desired resolution
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)   # (the camera may not honor it exactly)

        if not self.cap.isOpened():
            # If the camera didn't open (in use, doesn't exist, no permissions, etc.)
            # better to raise immediately instead of failing confusingly later.
            raise RuntimeError(f"Could not open camera with index {self.indice_camara}")

        return True

    def read_frame(self):
        """
        Reads a video frame from the camera.
        Returns the image (frame) or None if the read failed.
        """
        if self.cap is None:
            # Avoids a confusing error if someone forgets to call start() first.
            raise RuntimeError("The camera has not been started. Call start() first.")

        ret, frame = self.cap.read()  # ret = success or not; frame = the captured image

        if not ret:
            return None  # Can happen if the camera disconnects or there's a read error

        frame = cv2.flip(frame, 1)  # Mirror effect: feels more natural for the user
        return frame

    def release(self):
        """
        Releases the camera. Must be called when the program ends,
        so it becomes available to other applications.
        """
        if self.cap is not None:
            self.cap.release()  # Releases access to the camera hardware
            self.cap = None     # Back to the initial state, as before start()
