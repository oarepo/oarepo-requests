#
# Copyright (C) 2025 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

"""Notification generators related functionality for OARepo requests."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

log = logging.getLogger("oarepo_requests.notifications.generators")

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


def _extract_entity_email_data(entity: Any) -> dict[str, Any]:
    def _get(entity: Any, key: str) -> Any:
        if isinstance(entity, dict) and key in entity:
            return entity.get(key, None)
        return getattr(entity, key, None)

    def _add(entity: Any, key: str, res: dict[str, Any], transform: Callable = lambda x: x) -> Any:
        v = _get(entity, key)
        if v:
            res[key] = transform(v)
            return v
        return None

    ret = {}
    email = _add(entity, "email", ret)
    if not email:
        log.error(
            "Entity %s %s does not have email/emails attribute, skipping.",
            type(entity),
            entity,
        )
        return {}
    _add(entity, "preferences", ret, transform=lambda x: dict(x))
    _add(entity, "id", ret)

    return ret
