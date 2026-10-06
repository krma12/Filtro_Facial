import math

from filters.base_filter import Filter


class GlassesFilter(Filter):
    """
    AR filter that overlays glasses centered between the eyes, scaled to
    the distance between them, and rotated to match the head's tilt.
    """

    # Landmark indices for the outer corner of each eye (Mediapipe's
    # standard 468-point face mesh topology).
    OJO_IZQUIERDO_EXTERIOR = 33
    OJO_DERECHO_EXTERIOR = 263

    def apply(self, frame, landmarks):
        punto_izq = self._pixel_coordinates(frame, landmarks[self.OJO_IZQUIERDO_EXTERIOR])
        punto_der = self._pixel_coordinates(frame, landmarks[self.OJO_DERECHO_EXTERIOR])

        x_centro = (punto_izq[0] + punto_der[0]) // 2
        y_centro = (punto_izq[1] + punto_der[1]) // 2

        distancia_ojos = math.hypot(punto_der[0] - punto_izq[0], punto_der[1] - punto_izq[1])

        # Angle of the line between the eyes, relative to horizontal
        angulo = math.degrees(math.atan2(
            punto_der[1] - punto_izq[1],
            punto_der[0] - punto_izq[0],
        ))

        ancho = int(distancia_ojos * 2.2)
        alto = int(ancho * self.imagen.shape[0] / self.imagen.shape[1])

        return self.overlay_image(frame, x_centro, y_centro, ancho, alto, angulo)
