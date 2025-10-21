#
# Copyright (c) 2025 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Links Module for requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_records_resources.services.base.links import EndpointLink
from invenio_requests.resolvers.registry import ResolverRegistry

if TYPE_CHECKING:
    from collections.abc import Callable


# TODO: R02
class RefEndpointLink(EndpointLink):
    """Endpoint link that adds reference query string parameter to the URL."""

    @override
    def __init__(
        self,
        endpoint: str,
        *,
        when: Callable | None = None,
        vars: Callable | None = None,
        params: list[str] | None = None,
        ref_querystring: str,
    ):
        """Construct.

        :param endpoint: str. endpoint of the URL
        :param when: fn(obj, dict) -> bool, when the URL should be rendered
        :param vars: fn(obj, dict), mutate dict in preparation for expansion
        :param params: list, parameters (excluding querystrings) used for expansion
        :param ref_querystring: str, name of the querystring parameter to be added to the URL
        """
        super().__init__(endpoint, when, vars, params)
        self._ref_querystring = ref_querystring

    @override
    def expand(self, obj: Any, context: dict[str, Any]) -> str:
        """Expand the endpoint."""
        ret = super().expand(obj, context)
        topic_ref = ResolverRegistry.reference_entity(obj)
        if topic_ref is None:
            raise ValueError(f"Can't create link with unresolvable entity {obj}")
        return f"{ret}?{self._ref_querystring}={next(iter(topic_ref.keys()))}:{next(iter(topic_ref.values()))}"
