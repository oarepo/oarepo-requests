#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Configuration for the oarepo request service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, cast

from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink

from oarepo_requests.resolvers.ui import resolve

if TYPE_CHECKING:
    from invenio_requests.records.api import Request


class RequestEntityLink(RequestLink):
    """Link to an entity within a request."""

    def __init__(
        self,
        uritemplate: str,
        when: Callable | None = None,
        vars: dict | None = None,
        entity: str = "topic",
    ) -> None:
        """Create a new link."""
        super().__init__(uritemplate, when, vars)
        self.entity = entity

    def vars(self, record: Request, vars: dict) -> dict:
        """Expand the vars with the entity."""
        super().vars(record, vars)
        entity = self._resolve(record, vars)
        self._expand_entity(entity, vars)
        return vars

    def should_render(self, obj: Request, ctx: dict[str, Any]) -> bool:
        """Check if the link should be rendered."""
        if not super().should_render(obj, ctx):
            return False
        return bool(self.expand(obj, ctx))

    def _resolve(self, obj: Request, ctx: dict[str, Any]) -> dict:
        """Resolve the entity and put it into the context cache.

        :param obj: Request object
        :param ctx: Context cache
        :return: The resolved entity
        """
        reference_dict: dict = getattr(obj, self.entity).reference_dict
        key = "entity:" + ":".join(
            f"{x[0]}:{x[1]}" for x in sorted(reference_dict.items())
        )
        if key in ctx:
            return ctx[key]
        try:
            entity = cast(dict, resolve(ctx["identity"], reference_dict))
        except Exception:  # noqa
            entity = {}
        ctx[key] = entity
        return entity

    def _expand_entity(self, entity: Any, vars: dict) -> None:
        """Expand the entity links into the vars."""
        vars.update({f"entity_{k}": v for k, v in entity.get("links", {}).items()})

    def expand(self, obj: Request, context: dict[str, Any]) -> str:
        """Expand the URI Template."""
        # Optimization: pre-resolve the entity and put it into the shared context
        # under the key - so that it can be reused by other links
        self._resolve(obj, context)

        # now expand the link
        return super().expand(obj, context)


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    """Configuration for the oarepo request service."""

    service_id = "oarepo_requests"

    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
        "self_html": RequestLink("{+ui}/requests/{id}"),
        "topic": RequestEntityLink("{+entity_self}"),
        "topic_html": RequestEntityLink("{+entity_self_html}"),
        "created_by": RequestEntityLink("{+entity_self}", entity="created_by"),
        "created_by_html": RequestEntityLink(
            "{+entity_self_html}", entity="created_by"
        ),
        "receiver": RequestEntityLink("{+entity_self}", entity="receiver"),
        "receiver_html": RequestEntityLink("{+entity_self_html}", entity="receiver"),
    }
