import os

import cv2

from camara_manager import CameraManager
from face_detector import FaceDetector
from filter_manager import FilterManager
from filters.ears_filter import EarsFilter
from filters.glasses_filter import GlassesFilter
from filters.hat_filter import HatFilter
from filters.mustache_filter import MustacheFilter

RUTA_ASSETS = os.path.join(os.path.dirname(__file__), "assets")


class FacialFilterApp:
    """
    Main application: ties CameraManager, FaceDetector and FilterManager
    together and runs the live video loop.
    """

    def __init__(self, indice_camara=0):
        # Constructor: creates all the pieces the app needs. Nothing here
        # opens the camera or a window yet - that happens in run().

        self.camara = CameraManager(indice_camara=indice_camara)
        self.detector = FaceDetector()

        # Create each filter once, then reuse these same instances across
        # combos below, instead of loading the images more than once.
        lentes = GlassesFilter(os.path.join(RUTA_ASSETS, "lentes.png"))
        bigote = MustacheFilter(os.path.join(RUTA_ASSETS, "bigote.png"))
        orejas = EarsFilter(os.path.join(RUTA_ASSETS, "orejas.png"))
        sombrero = HatFilter(os.path.join(RUTA_ASSETS, "sombrero.png"))

        combos = [
            ("Glasses", [lentes]),
            ("Mustache", [bigote]),
            ("Ears", [orejas]),
            ("Hat", [sombrero]),
            ("Cool", [lentes, bigote]),
            ("Party", [sombrero, bigote]),
            ("Full look", [lentes, bigote, orejas, sombrero]),
        ]
        self.gestor_filtros = FilterManager(combos)

    def run(self):
        """
        Starts the camera and runs the main loop: read a frame, detect the
        face, apply the active filter, show it on screen, and react to key
        presses. Keeps running until the user quits.
        """
        self.camara.start()

        print("Press 'f' to switch filters, 'q' to quit.")

        while True:
            frame = self.camara.read_frame()
            if frame is None:
                print("Could not read frame from camera.")
                break

            landmarks = self.detector.detect(frame)
            frame = self.gestor_filtros.apply(frame, landmarks)

            texto = f"Filter: {self.gestor_filtros.nombre_actual}"
            cv2.putText(frame, texto, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Facial Filter App", frame)

            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q'):
                break
            elif tecla == ord('f'):
                self.gestor_filtros.siguiente_filtro()

        self.cerrar()

    def cerrar(self):
        """
        Releases the camera and the face detector's resources, and closes
        any open windows. Called automatically at the end of run().
        """
        self.camara.release()
        self.detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Which camera do you want to use?")
    print("1. Front camera")
    print("2. Back camera")

    opcion = input("Choose an option (1 or 2): ")

    indice_camara = 1 if opcion == "1" else 0  # 1 = front, 0 = back, as we confirmed earlier

    app = FacialFilterApp(indice_camara=indice_camara)
    app.run()
