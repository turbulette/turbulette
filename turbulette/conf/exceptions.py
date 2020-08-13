class NotReadyError(Exception):
    """A resource isn't created yet"""
    def __init__(self, resource: str):
        self.resource = resource
        super().__init__(f"{resource} isn't ready yet")

class ImproperlyConfigured(Exception):
    """Trubulette is somehow improperly configured"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)
