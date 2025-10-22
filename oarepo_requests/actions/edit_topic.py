#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for creating a draft of published record for editing metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from ..utils import get_draft_record_service
from .components import CreatedTopicComponent
from .generic import OARepoAcceptAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork

    from .components import RequestActionState


# TODO: snapshot
class EditTopicAcceptAction(OARepoAcceptAction):
    """Accept creation of a draft of a published record for editing metadata."""

    action_components = (CreatedTopicComponent,)

    @override
    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the action, creating a draft of the record for editing metadata."""
        topic_service = get_draft_record_service(state.topic)
        topic_service.edit(identity, state.topic["id"], uow=uow)
        super().apply(identity, state, uow, *args, **kwargs)
