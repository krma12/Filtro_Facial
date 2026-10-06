import math

from filters.base_filter import Filter


class EarsFilter(Filter):
    """
    AR filter that overlays ears above the forehead, scaled to the width
    of the face, and rotated to match the head's tilt.
    """

    # Landmark indices (Mediapipe's standard 468-point face mesh topology).
    FRENTE = 10
    MENTON = 152
    CARA_IZQUIERDA = 234
    CARA_DERECHA = 454
    OJO_IZQUIERDO_EXTERIOR = 33
    OJO_DERECHO_EXTERIOR = 263

    def apply(self, frame, landmarks):
        frente = self._pixel_coordinates(frame, landmarks[self.FRENTE])
        menton = self._pixel_coordinates(frame, landmarks[self.MENTON])
        cara_izq = self._pixel_coordinates(frame, landmarks[self.CARA_IZQUIERDA])
        cara_der = self._pixel_coordinates(frame, landmarks[self.CARA_DERECHA])
        ojo_izq = self._pixel_coordinates(frame, landmarks[self.OJO_IZQUIERDO_EXTERIOR])
        ojo_der = self._pixel_coordinates(frame, landmarks[self.OJO_DERECHO_EXTERIOR])

        ancho_cara = math.hypot(cara_der[0] - cara_izq[0], cara_der[1] - cara_izq[1])
        alto_cara = math.hypot(menton[0] - frente[0], menton[1] - frente[1])

        angulo = math.degrees(math.atan2(
            ojo_der[1] - ojo_izq[1],
            ojo_der[0] - ojo_izq[0],
        ))

        # The face mesh has no points above the hairline, so we push the
        # center up from the forehead landmark by a fraction of the face's
        # own height (this is a simplification: it doesn't account for
        # head roll in the offset itself, only in the final rotation).
        x_centro = frente[0]
        y_centro = int(frente[1] - alto_cara * 0.15)

        ancho = int(ancho_cara * 1.6)
        alto = int(ancho * self.imagen.shape[0] / self.imagen.shape[1])

        return self.overlay_image(frame, x_centro, y_centro, ancho, alto, angulo)
