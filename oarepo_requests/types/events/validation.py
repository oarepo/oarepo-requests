"""Validation of event types."""


def _serialized_topic_validator(value: str) -> str:
    """Validate the serialized topic. It must be a string with model and id separated by a single dot."""
    if len(value.split(".")) != 2:
        raise ValueError(
            "Serialized topic must be a string with model and id separated by a single dot."
        )
    return value
