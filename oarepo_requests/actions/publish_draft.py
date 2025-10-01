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

from invenio_access.permissions import system_identity
from invenio_i18n import _
from invenio_requests.records.api import Request
from oarepo_runtime.proxies import current_runtime

from oarepo_requests.errors import UnresolvedRequestsError, VersionAlreadyExists

from ..temp_utils import search_requests
from .components import CreatedTopicComponent
from .generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)

if TYPE_CHECKING:
    from flask_principal import Identity
    from invenio_db.uow import UnitOfWork
    from invenio_requests.customizations import RequestAction

    from .components import RequestActionState
else:
    RequestAction = object


class PublishMixin(RequestAction):
    """Mixin for publish actions."""

    def can_execute(self) -> bool:
        """Check if the action can be executed."""
        if not super().can_execute():
            return False

        try:
            from ..types.publish_draft import PublishDraftRequestType

            topic = self.request.topic.resolve()
            PublishDraftRequestType.validate_topic(system_identity, topic)
        except:  # noqa E722: used for displaying buttons, so ignore errors here
            return False
        return True


# TODO: snapshot
class PublishDraftSubmitAction(PublishMixin, OARepoSubmitAction):
    """Submit action for publishing draft requests."""

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Publish the draft."""
        if "payload" in self.request and "version" in self.request["payload"]:
            topic_service = current_runtime.get_record_service_for_record(state.topic)
            versions = topic_service.search_versions(identity, state.topic.pid.pid_value)
            versions_hits = versions.to_dict()["hits"]["hits"]
            for rec in versions_hits:
                if "version" in rec["metadata"]:
                    version = rec["metadata"]["version"]
                    if version == self.request["payload"]["version"]:
                        raise VersionAlreadyExists
            state.topic.metadata["version"] = self.request["payload"]["version"]
        # TODO: notification
        return super().apply(identity, state, uow, *args, **kwargs)


class PublishDraftAcceptAction(PublishMixin, OARepoAcceptAction):
    """Accept action for publishing draft requests."""

    name = _("Publish")

    action_components = (CreatedTopicComponent,)

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Publish the draft."""
        topic_service = current_runtime.get_record_service_for_record(state.topic)
        if not topic_service:
            raise KeyError(f"topic {state.topic} service not found")
        requests = search_requests(system_identity, state.topic)

        for result in requests._results:  # noqa SLF001
            if (
                result.type
                not in [
                    "publish_draft",
                    "publish_new_version",
                    "publish_changed_metadata",
                ]
                and result.is_open
                and Request.get_record(result.uuid)["status"]
                in (
                    "submitted",
                    "created",
                )
            ):
                # note: we can not use solely the result.is_open because changes may not be committed yet
                # to opensearch index. That's why we need to get the record from DB and re-check.
                raise UnresolvedRequestsError(action=str(self.name))
        id_ = state.topic["id"]

        published_topic = topic_service.publish(identity, id_, *args, uow=uow, expand=False, **kwargs)
        state.created_topic = published_topic._record  # noqa SLF001
        # TODO: topic update cascade?
        state.topic = published_topic._record  # noqa SLF001
        # TODO: notification
        return super().apply(identity, state, uow, *args, **kwargs)


class PublishDraftDeclineAction(OARepoDeclineAction):
    """Decline action for publishing draft requests."""

    name = _("Return for correction")

    def apply(
        self,
        identity: Identity,
        state: RequestActionState,
        uow: UnitOfWork,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Publish the draft."""
        # TODO: notification
        return super().apply(identity, state, uow, *args, **kwargs)
