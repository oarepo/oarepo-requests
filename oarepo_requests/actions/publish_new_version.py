#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for publishing draft requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from invenio_i18n import _
from invenio_records_resources.services.uow import RecordCommitOp

from ..utils import get_draft_record_service

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork

    from .components import RequestActionState


from .publish_draft import PublishDraftAcceptAction


class PublishNewVersionAcceptAction(PublishDraftAcceptAction):
    """Accept action for publishing draft requests."""

    name = _("Publish")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Publish the draft."""
        topic_service = get_draft_record_service(state.topic)

        if "payload" in self.request and "version" in self.request["payload"]:
            state.topic.metadata["version"] = self.request["payload"]["version"]
            uow.register(RecordCommitOp(state.topic, indexer=topic_service.indexer))

        return super().apply(identity, state, uow, *args, **kwargs)
