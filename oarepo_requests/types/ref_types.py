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

from invenio_communities.communities.entity_resolvers import CommunityResolver
from invenio_records_resources.references import RecordResolver
from invenio_requests.proxies import current_requests

from oarepo_requests.proxies import current_oarepo_requests


# TODO: we have to develop different method to allow only published_records/drafts; type_key loses discriminative value
class ModelRefTypes:
    """Class is used to define the allowed reference types for the topic reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_TOPICS).
    """

    def __init__(self, published: bool = False, draft: bool = False) -> None:
        """Initialize the class."""
        self.published = published
        self.draft = draft

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        ret: list[str] = []
        resolvers = current_requests.entity_resolvers_registry
        if resolvers is None:
            return ret
        for resolver in resolvers:
            if not isinstance(resolver, RecordResolver) or isinstance(
                resolver, CommunityResolver
            ):  # TODO: CommunityResolver technically is a RecordResolver
                continue
            ret.append(resolver.type_key)
            """
            supports_drafts: bool = hasattr(resolver, "draft_cls")
            if (self.published and not supports_drafts) or (self.draft and supports_drafts):
                ret.append(resolver.type_key)
            """
        return ret


class ReceiverRefTypes:
    """Class is used to define the allowed reference types for the receiver reference.

    The list of ref types is taken from the configuration (configuration key REQUESTS_ALLOWED_RECEIVERS).
    """

    def __get__(self, obj: Self, owner: type[Self]) -> list[str]:
        """Property getter, returns the list of allowed reference types."""
        return current_oarepo_requests.allowed_receiver_ref_types
