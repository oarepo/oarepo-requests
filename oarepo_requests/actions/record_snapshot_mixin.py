from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any

from flask_principal import PermissionDenied
from oarepo_runtime.proxies import current_runtime

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_drafts_resources.records import Record
    from invenio_records_resources.services.uow import UnitOfWork
    from invenio_requests.customizations.actions import RequestAction

    from .components import RequestActionState


class RecordSnapshotMixin:
    def apply(
        self: RequestAction,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> Record:
        """Take snapshot of the record."""
        super_apply = super().apply(identity, state.request_type, state.topic, uow, *args, **kwargs)

        service = current_runtime.get_record_service_for_record(state.topic)

        with suppress(PermissionDenied):
            if not state.topic.is_draft:
                ret = service.read(identity, state.topic.pid.pid_value)
            else:
                ret = service.read_draft(identity, state.topic.pid.pid_value)

            from oarepo_requests.snapshots import create_snapshot_and_possible_event

            create_snapshot_and_possible_event(state.topic, ret.to_dict()["metadata"], self.request.id)

        return super_apply
