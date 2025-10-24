#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Classes that define allowed reference types for the topic and receiver references."""

from __future__ import annotations

from typing import Self

from oarepo_runtime import current_runtime

from oarepo_requests.proxies import current_oarepo_requests


class ModelRefTypes:
    """Class is used to define the allowed reference types for the topic reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_TOPICS).
    """

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        return [model.entity_type for model in current_runtime.rdm_models]


class ReceiverRefTypes:
    """Class is used to define the allowed reference types for the receiver reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_RECEIVERS).
    """

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        return current_oarepo_requests.allowed_receiver_ref_types
