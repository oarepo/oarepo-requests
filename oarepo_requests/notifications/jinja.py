#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Jinja utils."""

from __future__ import annotations

from typing import Any, cast

from invenio_i18n import gettext as _


def get_request_user_name(user: dict[str, Any] | str) -> str:
    """Return the best available display name for user in request."""
    # TODO: for consideration: this was in the original string but imo it should not happen in the intended use case
    if isinstance(user, str):
        return user

    if full_name := user.get("profile", {}).get("full_name"):
        return cast("str", full_name)

    if user.get("preferences", {}).get("email_visibility") == "public" and user.get("email"):
        return cast("str", user.get("email"))

    return cast("str", user.get("username") or _("User {user_id}").format(user_id=user.get("id")))
