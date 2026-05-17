import json
from decimal import Decimal
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    """
    Safe JSON encoder for system-wide use.
    """

    def default(self, o):  # MUST be 'o' not 'obj'
        if isinstance(o, Decimal):
            return str(o)

        if isinstance(o, UUID):
            return str(o)

        return super().default(o)