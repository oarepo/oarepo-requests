#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for creating a new version of a published record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from oarepo_runtime.proxies import current_runtime

from .components import CreatedTopicComponent
from .generic import OARepoAcceptAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork

    from .components import RequestActionState


# TODO: snapshot
class NewVersionAcceptAction(OARepoAcceptAction):
    """Accept creation of a new version of a published record."""

    action_components = (CreatedTopicComponent,)

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the action, creating a new version of the record."""
        topic_service = current_runtime.get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")

        new_version_topic = topic_service.new_version(identity, state.topic["id"], uow=uow)
        state.created_topic = new_version_topic._record  # noqa SLF001
        if (
            "payload" in self.request
            and "keep_files" in self.request["payload"]
            and self.request["payload"]["keep_files"] == "yes"
        ):
            topic_service.import_files(identity, new_version_topic.id)

        return super().apply(identity, state, uow, *args, **kwargs)
