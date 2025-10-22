#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Helper functions to convert identity to entity references."""

from __future__ import annotations

from typing import TYPE_CHECKING

# TODO: possibly not used
if TYPE_CHECKING:
    from flask_principal import Identity


def user_mappings(identity: Identity) -> list[dict[str, str]]:
    """Convert identity to entity references of type "user"."""
    return [{"user": identity.id}]


def group_mappings(identity: Identity) -> list[dict[str, str]]:
    """Convert groups of the identity to entity references of type "group"."""
    roles = [n.value for n in identity.provides if n.method == "role"]
    return [{"group": role_id} for role_id in roles]
