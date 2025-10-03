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

from invenio_drafts_resources.services.records.service import RecordService
from oarepo_runtime.proxies import current_runtime

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
        topic_service = current_runtime.get_record_service_for_record(
            state.topic
        )  # TODO: this should be a draft service

        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")
        if not isinstance(topic_service, RecordService):
            raise TypeError("Draft service required for editing records.")
        created_topic = topic_service.edit(identity, state.topic["id"], uow=uow)
        state.created_topic = created_topic._record  # noqa SLF001
        super().apply(identity, state, uow, *args, **kwargs)
