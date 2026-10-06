import cv2


class Filter:
    """
    Base class for every AR filter (mustache, glasses, ears, hat, etc.).
    Loads the accessory image once; each specific filter decides where
    and how big to draw it by overriding apply().
    """

    def __init__(self, ruta_imagen):
        # Constructor: loads the accessory image and keeps it ready to use.
        # The actual positioning logic lives in each subclass, not here.

        self.ruta_imagen = ruta_imagen
        self.imagen = cv2.imread(ruta_imagen, cv2.IMREAD_UNCHANGED)  # keeps the alpha (transparency) channel

        if self.imagen is None:
            # cv2.imread doesn't raise an error on a bad path, it just returns None,
            # which would cause a confusing crash later if we didn't catch it here.
            raise FileNotFoundError(f"Could not load filter image at: {ruta_imagen}")

    def overlay_image(self, frame, x_centro, y_centro, ancho, alto, angulo=0):
        """
        Overlays self.imagen (resized to ancho x alto, then rotated by
        angulo degrees) onto frame, centered at (x_centro, y_centro) in
        pixel coordinates. Respects transparency and automatically clips
        if part of the accessory would fall outside the frame. Modifies
        frame in place and also returns it.
        """
        imagen_redimensionada = cv2.resize(self.imagen, (ancho, alto))

        if angulo != 0:
            matriz_rotacion = cv2.getRotationMatrix2D((ancho / 2, alto / 2), -angulo, 1.0)
            imagen_redimensionada = cv2.warpAffine(
                imagen_redimensionada, matriz_rotacion, (ancho, alto),
                borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)  # keep the new corners transparent
            )

        # Top-left corner the accessory would occupy if nothing were clipped
        x1 = x_centro - ancho // 2
        y1 = y_centro - alto // 2
        x2 = x1 + ancho
        y2 = y1 + alto

        alto_frame, ancho_frame = frame.shape[:2]

        # Clip that region to the frame's actual boundaries
        x1_frame = max(x1, 0)
        y1_frame = max(y1, 0)
        x2_frame = min(x2, ancho_frame)
        y2_frame = min(y2, alto_frame)

        if x1_frame >= x2_frame or y1_frame >= y2_frame:
            return frame  # Completely off-screen, nothing to draw

        # The matching region within the (possibly clipped) accessory image
        x1_img = x1_frame - x1
        y1_img = y1_frame - y1
        x2_img = x1_img + (x2_frame - x1_frame)
        y2_img = y1_img + (y2_frame - y1_frame)

        region_imagen = imagen_redimensionada[y1_img:y2_img, x1_img:x2_img]
        region_frame = frame[y1_frame:y2_frame, x1_frame:x2_frame]

        alfa = region_imagen[:, :, 3] / 255.0  # alpha channel, normalized to 0-1
        alfa = alfa[:, :, None]  # add a dimension so it broadcasts against the 3 BGR channels

        region_frame[:] = (alfa * region_imagen[:, :, :3] + (1 - alfa) * region_frame).astype("uint8")

        return frame

    def _pixel_coordinates(self, frame, landmark):
        """
        Converts one landmark's normalized (0 to 1) coordinates into real
        pixel coordinates for the given frame. Same formula as
        FaceDetector.get_landmark_coordinates(), kept separate on purpose
        so Filter doesn't need to depend on FaceDetector.
        """
        alto, ancho = frame.shape[:2]
        return (int(landmark.x * ancho), int(landmark.y * alto))

    def apply(self, frame, landmarks):
        """
        Draws this filter on top of frame, using the detected face landmarks
        to decide where. Every subclass MUST override this method.
        """
        raise NotImplementedError("Subclasses of Filter must implement apply().")
