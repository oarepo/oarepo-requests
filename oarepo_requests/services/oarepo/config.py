#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration for the oarepo request service."""

from __future__ import annotations

import logging

from invenio_requests.services import RequestsServiceConfig

from oarepo_requests.services.search import EnhancedRequestSearchOptions

log = logging.getLogger(__name__)

"""
def override_invenio_requests_config(state: BlueprintSetupState, *args: Any, **kwargs: Any) -> None:  # noqa ARG001

    with state.app.app_context():
        # this monkey patch should be done better (support from invenio)
        RequestsServiceConfig.search = EnhancedRequestSearchOptions
        RequestsResourceConfig.request_search_args = ExtendedRequestSearchRequestArgsSchema
        # add extra links to the requests
        for k, v in OARepoRequestsServiceConfig.links_item.items():
            if k not in RequestsServiceConfig.links_item:
                RequestsServiceConfig.links_item[k] = v

        class LazySerializer:
            def __init__(self, serializer_cls: type[BaseSerializer]) -> None:
                self.serializer_cls = serializer_cls

            @cached_property
            def __instance(self) -> BaseSerializer:
                return self.serializer_cls()

            @property
            def serialize_object_list(self) -> Callable:
                return self.__instance.serialize_object_list

            @property
            def serialize_object(self) -> Callable:
                return self.__instance.serialize_object

        # TODO: patch response handlers

        from invenio_i18n import _
        from invenio_requests.proxies import current_request_type_registry
        from invenio_requests.services.requests.facets import status, type  # noqa A004

        status._value_labels = {  # noqa SLF001
            "submitted": _("Submitted"),
            "expired": _("Expired"),
            "accepted": _("Accepted"),
            "declined": _("Declined"),
            "cancelled": _("Cancelled"),
            "created": _("Created"),
        }
        status._label = _("Request status")  # noqa SLF001

        # add extra request types dynamically
        type._value_labels = {rt.type_id: rt.name for rt in iter(current_request_type_registry)}  # noqa SLF001
        type._label = _("Type")  # noqa SLF001
"""


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    search = EnhancedRequestSearchOptions
