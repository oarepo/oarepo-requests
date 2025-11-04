#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for publishing new version draft requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from invenio_i18n import _
from invenio_records_resources.services.uow import RecordCommitOp

from ..utils import get_draft_record_service

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork


from .publish_draft import PublishDraftAcceptAction


class PublishNewVersionAcceptAction(PublishDraftAcceptAction):
    """Accept action for publishing new version draft requests."""

    name = _("Publish")

    @override
    def apply(
        self,
        identity: Identity,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if "payload" in self.request and "version" in self.request["payload"]:
            topic_service = get_draft_record_service(self.topic)
            self.topic.metadata["version"] = self.request["payload"]["version"]
            uow.register(RecordCommitOp(self.topic, indexer=topic_service.indexer))
        super().apply(identity, uow, *args, **kwargs)
