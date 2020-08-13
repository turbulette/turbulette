class TurbuletteAppError(Exception):
    def __init__(self, app_label: str, message: str):
        self.app_label = app_label
        super().__init__(self, f"[App {self.app_label}] : {message}")

class RegistryError(Exception):
    pass
