#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for creating a new version of a published record."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from oarepo_runtime.typing import record_from_result

from ..utils import get_draft_record_service, ref_to_str, reference_entity
from .generic import OARepoAcceptAction

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork


# TODO: snapshot
class NewVersionAcceptAction(OARepoAcceptAction):
    """Accept creation of a new version of a published record."""

    @override
    def apply(
        self,
        identity: Identity,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Apply the action, creating a new version of the record."""
        topic_service = get_draft_record_service(self.topic)
        new_version_topic = topic_service.new_version(
            identity, self.topic["id"], uow=uow
        )
        created_topic = record_from_result(new_version_topic)
        if (
            "payload" in self.request
            and "keep_files" in self.request["payload"]
            and self.request["payload"]["keep_files"] == "yes"
        ):
            topic_service.import_files(identity, new_version_topic.id)
        if "payload" not in self.request:
            self.request["payload"] = {}
        # payload only allows strings
        self.request["payload"]["created_topic"] = ref_to_str(
            reference_entity(created_topic)
        )
