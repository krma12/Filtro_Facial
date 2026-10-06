class FilterManager:
    """
    Keeps track of the available filter combos and which one (if any) is
    currently active, so main.py doesn't have to juggle that state itself.
    A "combo" is one or more filters applied together.
    """

    def __init__(self, combos):
        # Constructor: stores the list of available combos.
        # combos: a list of (nombre, lista_de_filtros) pairs. A combo can
        # have just one filter (e.g. just glasses) or several at once
        # (e.g. glasses + mustache).

        self.combos = combos
        self.indice_actual = -1  # -1 means "no filter active" (plain video)

    @property
    def filtros_actuales(self):
        """Returns the list of Filter instances in the active combo (possibly empty)."""
        if self.indice_actual == -1:
            return []
        _, filtros = self.combos[self.indice_actual]
        return filtros

    @property
    def nombre_actual(self):
        """Returns the currently active combo's display name."""
        if self.indice_actual == -1:
            return "None"
        nombre, _ = self.combos[self.indice_actual]
        return nombre

    def siguiente_filtro(self):
        """
        Cycles to the next combo in the list. After the last one, it
        wraps around to "no filter" (-1), then back to the first combo.
        """
        self.indice_actual += 1
        if self.indice_actual >= len(self.combos):
            self.indice_actual = -1

    def apply(self, frame, landmarks):
        """
        Applies every filter in the active combo to frame, in order, if a
        face was actually detected. Otherwise returns frame unchanged.
        """
        if landmarks is None:
            return frame

        for filtro in self.filtros_actuales:
            frame = filtro.apply(frame, landmarks)

        return frame
