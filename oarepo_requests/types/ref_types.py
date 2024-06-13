from oarepo_requests.proxies import current_oarepo_requests


class ModelRefTypes:
    """
    This class is used to define the allowed reference types for the topic reference.
    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_TOPICS).
    """

    def __get__(self, obj, owner):
        """Property getter, returns the list of allowed reference types."""
        return current_oarepo_requests.allowed_topic_ref_types


class ReceiverRefTypes:
    """
    This class is used to define the allowed reference types for the receiver reference.
    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_RECEIVERS).
    """

    def __get__(self, obj, owner):
        """Property getter, returns the list of allowed reference types."""
        return current_oarepo_requests.allowed_receiver_ref_types
