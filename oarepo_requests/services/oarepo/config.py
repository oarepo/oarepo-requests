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
from typing import TYPE_CHECKING, Any

from invenio_pidstore.errors import PersistentIdentifierError
from invenio_records_resources.services.base.links import Link
from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink

from oarepo_requests.resolvers.ui import resolve

if TYPE_CHECKING:
    from invenio_requests.records.api import Request
log = logging.getLogger(__name__)


class RequestEntityLinks(Link):
    """Utility class for keeping track of and resolve links."""

    def _resolve(self, obj: Request, ctx: dict[str, Any]) -> dict:
        """Resolve the entity and put it into the context cache.

        :param obj: Request object
        :param ctx: Context cache
        :return: The resolved entity
        """
        reference_dict: dict = getattr(obj, self._entity).reference_dict
        key = "entity:" + ":".join(
            f"{x[0]}:{x[1]}" for x in sorted(reference_dict.items())
        )
        if key in ctx:
            return ctx[key]
        try:
            entity = resolve(ctx["identity"], reference_dict)
        except Exception as e:  # noqa
            if not isinstance(e, PersistentIdentifierError):
                log.exception(
                    "Error resolving %s for identity %s",
                    reference_dict,
                    ctx["identity"],
                )
            entity = {"links": {}}
        ctx[key] = entity
        return entity

    def __init__(self, entity: str, when: callable = None):
        """Constructor."""
        self._entity = entity
        self._when_func = when

    def expand(self, obj: Request, context: dict) -> dict:
        """Create the request links."""
        res = {}
        res.update(self._resolve(obj, context)["links"])

        if hasattr(obj.type, "extra_request_links"):
            entity = self._resolve(obj, context)
            res.update(
                obj.type.extra_request_links(
                    request=obj,
                    **(context | {"cur_entity": entity, "entity_type": self._entity}),
                )
            )

        return res


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    service_id = "oarepo_requests"

    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
        "self_html": RequestLink("{+ui}/requests/{id}"),
        "topic": RequestEntityLinks(entity="topic"),
        "created_by": RequestEntityLinks(entity="created_by"),
        "receiver": RequestEntityLinks(entity="receiver"),
    }
