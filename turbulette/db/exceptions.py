class DoesNotExist(Exception):
    """Raised when a query on the model fail because no row was returned from the database."""

    def __init__(self, obj):
        # Handle classmethod calls
        if isinstance(obj, type):
            message = f"{obj.__name__} does not exist"
        else:
            message = f"{type(obj).__name__} does not exist"

        super().__init__(message)
