from backend.config_system.core.schema import ConfigType


class ValidationService:

    @staticmethod
    def validate(definition, value):
        expected_type = definition.config_type

        if expected_type == ConfigType.BOOL:
            if not isinstance(value, bool):
                raise ValueError("Expected bool")

        elif expected_type == ConfigType.INT:
            if not isinstance(value, int):
                raise ValueError("Expected int")

        elif expected_type == ConfigType.FLOAT:
            if not isinstance(value, float):
                raise ValueError("Expected float")

        elif expected_type == ConfigType.STRING:
            if not isinstance(value, str):
                raise ValueError("Expected string")

        elif expected_type == ConfigType.LIST:
            if not isinstance(value, list):
                raise ValueError("Expected list")

        elif expected_type == ConfigType.JSON:
            if not isinstance(value, dict):
                raise ValueError("Expected dict")

        if definition.validator:
            if not definition.validator(value):
                raise ValueError(
                    f"Custom validation failed for {definition.key}"
                )