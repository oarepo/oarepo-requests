def _serialized_topic_validator(value):
    if len(value.split(".")) != 2:
        raise ValueError(
            "Serialized topic must be a string with model and id separated by a single dot."
        )
    return value
