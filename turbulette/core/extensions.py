from ariadne.types import Extension
from turbulette.core.errors import errors


class PolicyExtension(Extension):
    def format(self, context):
        messages = None
        if errors:
            messages = {**errors}
            errors.clear()
        return messages