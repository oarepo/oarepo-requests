#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo-Requests extension."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from deepmerge import conservative_merger
from invenio_base.utils import obj_or_import_string
from invenio_requests.customizations import EventType
from invenio_requests.proxies import (
    current_event_type_registry,
    current_request_type_registry,
)

if TYPE_CHECKING:
    from flask import Flask
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_requests.customizations import RequestType

    from oarepo_requests.actions.components import RequestActionComponent


class _OARepoRequestsState:
    def __init__(self, app: Flask):
        """Initialize state.

        :param app: An instance of :class:`~flask.app.Flask`.
        :param entry_point_group_mappings:
            The entrypoint group name to load mappings.
        :param entry_point_group_templates:
            The entrypoint group name to load templates.
        """
        self.app = app

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.app = app
        app.extensions["oarepo-requests"] = self

    @property
    def allowed_receiver_ref_types(self) -> list[str]:
        """Return a list of allowed receiver entity reference types.

        This value is taken from the configuration key REQUESTS_ALLOWED_RECEIVERS.
        """
        return cast("list[str]", self.app.config.get("REQUESTS_ALLOWED_RECEIVERS", []))

    def action_components(self) -> list[type[RequestActionComponent]]:
        """Return components for the given action."""
        return cast(
            "list[type[RequestActionComponent]]",
            self.app.config["REQUESTS_ACTION_COMPONENTS"],
        )

    def default_request_receiver(
        self,
        identity: Identity,
        request_type: RequestType,
        record: Record,
        creator: dict[str, str] | Identity,
        data: dict,
    ) -> dict[str, str] | None:
        """Return the default receiver for the request.

        Gets the default receiver for the request based on the request type, record and data.
        It is used when the receiver is not explicitly set when creating a request. It does so
        by taking a function from the configuration under the key OAREPO_REQUESTS_DEFAULT_RECEIVER
        and calling it with the given parameters.

        :param identity: Identity of the user creating the request.
        :param request_type: Type of the request.
        :param record: Record the request is about.
        :param creator: Creator of the request.
        :param data: Payload of the request.
        """
        return obj_or_import_string(self.app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"])(  # type: ignore[no-any-return]
            identity=identity,
            request_type=request_type,
            record=record,
            creator=creator,
            data=data,
        )


class OARepoRequests:
    """OARepo-Requests extension."""

    def __init__(self, app: Flask | None = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization.

        :param app: An instance of :class:`~flask.app.Flask`.
        """
        self.init_config(app)
        state = _OARepoRequestsState(app)
        self._state = app.extensions["oarepo-requests"] = state

    def __getattr__(self, name: str):
        """Proxy to state object."""
        return getattr(self._state, name, None)

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        from . import config

        app.config.setdefault("OAREPO_REQUESTS_DEFAULT_RECEIVER", None)
        app.config.setdefault("REQUESTS_ALLOWED_RECEIVERS", []).extend(config.REQUESTS_ALLOWED_RECEIVERS)

        app.config.setdefault("PUBLISH_REQUEST_TYPES", config.PUBLISH_REQUEST_TYPES)

        # do not overwrite user's stuff
        app_default_workflow_events = app.config.setdefault("DEFAULT_WORKFLOW_EVENTS", {})
        for k, v in config.DEFAULT_WORKFLOW_EVENTS.items():
            if k not in app_default_workflow_events:
                app_default_workflow_events[k] = v

        # let the user override the action components
        app.config.setdefault("REQUESTS_ACTION_COMPONENTS", []).extend(config.REQUESTS_ACTION_COMPONENTS)

        app_notification_recipient_resolvers = app.config.setdefault("NOTIFICATION_RECIPIENTS_RESOLVERS", {})
        app.config["NOTIFICATION_RECIPIENTS_RESOLVERS"] = conservative_merger.merge(
            app_notification_recipient_resolvers, config.NOTIFICATION_RECIPIENTS_RESOLVERS
        )

        app_notification_builders = app.config.setdefault("NOTIFICATIONS_BUILDERS", {})
        app_notification_backends = app.config.setdefault("NOTIFICATIONS_BACKENDS", {})

        app.config["NOTIFICATIONS_BUILDERS"] = conservative_merger.merge(
            app_notification_builders, config.NOTIFICATIONS_BUILDERS
        )
        app.config["NOTIFICATIONS_BACKENDS"] = conservative_merger.merge(
            app_notification_backends, config.NOTIFICATIONS_BACKENDS
        )


def api_finalize_app(app: Flask) -> None:
    """Finalize app."""
    finalize_app(app)


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    # TODO: temporary before invenio fix
    to_remove = [t for t in current_request_type_registry if isinstance(t, EventType)]
    for type_ in to_remove:
        current_request_type_registry._registered_types.pop(type_.type_id)  # noqa SLF001 # type: ignore[reportAttributeAccessIssue]
        current_event_type_registry.register_type(type_)

    ext = app.extensions["oarepo-requests"]
    ext.notification_recipients_resolvers_registry = app.config["NOTIFICATION_RECIPIENTS_RESOLVERS"]

    invenio_notifications = app.extensions["invenio-notifications"]
    invenio_notifications.init_manager(app)
