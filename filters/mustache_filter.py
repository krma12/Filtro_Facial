import math

from filters.base_filter import Filter


class MustacheFilter(Filter):
    """
    AR filter that overlays a mustache just below the nose, scaled to the
    width of the mouth, and rotated to match the head's tilt.
    """

    # Landmark indices (Mediapipe's standard 468-point face mesh topology).
    DEBAJO_NARIZ = 2
    BOCA_IZQUIERDA = 61
    BOCA_DERECHA = 291

    def apply(self, frame, landmarks):
        punto_centro = self._pixel_coordinates(frame, landmarks[self.DEBAJO_NARIZ])
        boca_izq = self._pixel_coordinates(frame, landmarks[self.BOCA_IZQUIERDA])
        boca_der = self._pixel_coordinates(frame, landmarks[self.BOCA_DERECHA])

        ancho_boca = math.hypot(boca_der[0] - boca_izq[0], boca_der[1] - boca_izq[1])

        angulo = math.degrees(math.atan2(
            boca_der[1] - boca_izq[1],
            boca_der[0] - boca_izq[0],
        ))

        ancho = int(ancho_boca * 1.65)  # a bit wider than the mouth itself
        alto = int(ancho * self.imagen.shape[0] / self.imagen.shape[1])

        return self.overlay_image(frame, punto_centro[0], punto_centro[1], ancho, alto, angulo)
