class ImproperlyConfigured(Exception):
    """Trubulette is somehow improperly configured."""

    def __init__(self, message):
        self.message = message
        super().__init__(message)
