#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Actions for delete published record request."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, override

from .generic import OARepoAcceptAction, OARepoDeclineAction

if TYPE_CHECKING:
    from flask_principal import Identity

from typing import TYPE_CHECKING

from invenio_db import db
from invenio_i18n import _
from oarepo_runtime.proxies import current_runtime
from oarepo_runtime.typing import record_from_result

if TYPE_CHECKING:
    from flask_principal import Identity


if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_rdm_records.services.services import RDMRecordService


class DeletePublishedRecordAcceptAction(OARepoAcceptAction):
    """Accept request for deletion of a published record and delete the record."""

    name = _("Permanently delete")

    @override
    def apply(
        self,
        identity: Identity,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        topic = self.topic
        topic_service = current_runtime.get_record_service_for_record(topic)
        if not topic_service:
            raise KeyError(f"topic {topic} service not found")
        if hasattr(topic_service, "delete_record"):
            topic_service = cast("RDMRecordService", topic_service)
            from flask import current_app

            oarepo = current_app.extensions["oarepo-runtime"]
            resource_config = oarepo.models_by_record_class[topic_service.record_cls].resource_config

            citation_text = "Citation unavailable."
            if resource_config and "text/x-iso-690+plain" in resource_config.response_handlers:
                citation_text = resource_config.response_handlers["text/x-iso-690+plain"].serializer.serialize_object(
                    topic
                )

            data = {
                "removal_reason": {"id": self.request["payload"]["removal_reason"]},
                "citation_text": citation_text,
                "note": self.request["payload"].get("note", ""),
                "is_visible": True,
            }
            self.topic = record_from_result(topic_service.delete_record(identity, topic["id"], data))
            db.session.commit()
        else:
            topic_service.delete(identity, topic["id"], *args, uow=uow, **kwargs)

        # TODO: notifications, cascade cancel?


class DeletePublishedRecordDeclineAction(OARepoDeclineAction):
    """Decline request for deletion of a published record."""

    name = _("Keep the record")
