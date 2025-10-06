#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""OARepo-Requests extension."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, cast

import importlib_metadata
from deepmerge import conservative_merger
from invenio_base.utils import obj_or_import_string

from oarepo_requests import config
from oarepo_requests.cli import oarepo_requests  # noqa
from oarepo_requests.resources.oarepo.config import OARepoRequestsResourceConfig
from oarepo_requests.resources.oarepo.resource import OARepoRequestsResource

if TYPE_CHECKING:
    from collections.abc import Callable

    from flask import Flask
    from flask_principal import Identity
    from invenio_records_resources.records.api import Record
    from invenio_requests.customizations import RequestType
    from invenio_requests.customizations.actions import RequestAction

    from oarepo_requests.actions.components import RequestActionComponent


class OARepoRequests:
    """OARepo-Requests extension."""

    def __init__(self, app: Flask | None = None) -> None:
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flask application initialization."""
        self.app = app
        self.init_config(app)
        self.init_resources(app)
        app.extensions["oarepo-requests"] = self

    @property
    def ui_serialization_referenced_fields(self) -> list[str]:
        """Request fields containing  that should be serialized in the UI.

        These fields will be dereferenced, serialized to UI using one of the entity_reference_ui_resolvers
        and included in the serialized request.
        """
        return cast("list[str]", self.app.config["REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS"])

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

    @property
    def allowed_receiver_ref_types(self) -> list[str]:
        """Return a list of allowed receiver entity reference types.

        This value is taken from the configuration key REQUESTS_ALLOWED_RECEIVERS.
        """
        return cast("list[str]", self.app.config.get("REQUESTS_ALLOWED_RECEIVERS", []))

    @cached_property
    def identity_to_entity_references_functions(self) -> list[Callable]:
        """Return a list of functions that map identity to entity references.

        These functions are used to map the identity of the user to entity references
        that represent the needs of the identity. The functions are taken from the entrypoints
        registered under the group oarepo_requests.identity_to_entity_references.
        """
        group_name = "oarepo_requests.identity_to_entity_references"
        return [x.load() for x in importlib_metadata.entry_points().select(group=group_name)]

    def identity_to_entity_references(self, identity: Identity) -> list[dict[str, str]]:
        """Map the identity to entity references."""
        ret = [
            mapping_fnc(identity)
            for mapping_fnc in (self.identity_to_entity_references_functions)
            if mapping_fnc(identity)
        ]
        flattened_ret = []
        for mapping_result in ret:
            if mapping_result:
                flattened_ret += mapping_result
        return flattened_ret

    def init_resources(self, app: Flask) -> None:
        """Init resources."""
        # TODO: import invenio
        self.requests_resource = OARepoRequestsResource(
            service=config.REQUESTS_SERVICE_CLASS(config.REQUESTS_SERVICE_CONFIG_CLASS.build(app)),
            config=OARepoRequestsResourceConfig.build(app),
        )
        # TODO: event resource

    # TODO: do we want this configurable by actual actions? - ie. vs the "specific" hardcoded in action code
    def action_components(self, action: RequestAction) -> list[type[RequestActionComponent]]:
        """Return components for the given action."""
        components: (
            dict[str, list[type[RequestActionComponent]]]
            | Callable[[RequestAction], list[type[RequestActionComponent]]]
        ) = self.app.config["REQUESTS_ACTION_COMPONENTS"]
        if callable(components):
            """
             Type "object | list[type[RequestActionComponent]]" is not assignable to return type
             "list[type[RequestActionComponent]]"
                Type "object | list[type[RequestActionComponent]]" is not assignable to type
                "list[type[RequestActionComponent]]" "object" is not assignable to "list[type[RequestActionComponent]]"
            idk why it complains about this, why object | ...
            """
            return components(action)  # type: ignore[reportReturnType]
        return components[action.status_to]

    def init_config(self, app: Flask) -> None:
        """Initialize configuration."""
        from . import config

        app.config.setdefault("OAREPO_REQUESTS_DEFAULT_RECEIVER", None)
        app.config.setdefault("REQUESTS_SERVICE_CLASS", config.REQUESTS_SERVICE_CLASS)
        app.config.setdefault("REQUESTS_SERVICE_CONFIG_CLASS", config.REQUESTS_SERVICE_CONFIG_CLASS)
        app.config.setdefault("REQUESTS_ALLOWED_RECEIVERS", []).extend(config.REQUESTS_ALLOWED_RECEIVERS)
        app.config.setdefault("REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS", []).extend(
            config.REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS
        )
        app.config.setdefault("SNAPSHOT_CLEANUP_DAYS", config.SNAPSHOT_CLEANUP_DAYS)

        app.config.setdefault("PUBLISH_REQUEST_TYPES", config.PUBLISH_REQUEST_TYPES)

        # do not overwrite user's stuff
        app_default_workflow_events = app.config.setdefault("DEFAULT_WORKFLOW_EVENTS", {})
        for k, v in config.DEFAULT_WORKFLOW_EVENTS.items():
            if k not in app_default_workflow_events:
                app_default_workflow_events[k] = v

        # let the user override the action components
        rac = app.config.setdefault("REQUESTS_ACTION_COMPONENTS", {})
        for k, v in config.REQUESTS_ACTION_COMPONENTS.items():
            if k not in rac:
                rac[k] = v

        app_registered_event_types = app.config.setdefault("REQUESTS_REGISTERED_EVENT_TYPES", [])
        for event_type in config.REQUESTS_REGISTERED_EVENT_TYPES:
            if event_type not in app_registered_event_types:
                app_registered_event_types.append(event_type)

        # TODO: notifications config
        app_registered_event_types = app.config.setdefault("NOTIFICATION_RECIPIENTS_RESOLVERS", {})

        # can't set default config directly because it might be initialized to {} in invenio-notifications
        app.config.setdefault("NOTIFICATIONS_BUILDERS", {})
        app_notification_backends = app.config.setdefault("NOTIFICATIONS_BACKENDS", {})

        app.config["NOTIFICATIONS_BACKENDS"] = conservative_merger.merge(
            app_notification_backends, config.NOTIFICATIONS_BACKENDS
        )


def api_finalize_app(app: Flask) -> None:
    """Finalize app."""
    finalize_app(app)


def finalize_app(app: Flask) -> None:
    """Finalize app."""
    from invenio_requests.proxies import current_event_type_registry

    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.

    ext = app.extensions["oarepo-requests"]

    # TODO: i have to do this cause there is bug in invenio-requests for events
    # but imo this is better than entrypoints
    for type_ in app.config["REQUESTS_REGISTERED_EVENT_TYPES"]:
        current_event_type_registry.register_type(type_)

    ext.notification_recipients_resolvers_registry = app.config["NOTIFICATION_RECIPIENTS_RESOLVERS"]

    invenio_notifications = app.extensions[
        "invenio-notifications"
    ]  # initialized during ext in invenio notifications, our config might not be loaded
    notification_resolvers = {er.type_key: er for er in app.config["NOTIFICATIONS_ENTITY_RESOLVERS"]}
    invenio_notifications.entity_resolvers = notification_resolvers
    invenio_notifications.init_manager(app)  # race condition between config init and original init_manager
