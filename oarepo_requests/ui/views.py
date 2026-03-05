#
# Copyright (c) 2026 CESNET z.s.p.o.
#
# This file is a part of oarepo-requests (see https://github.com/oarepo/oarepo-requests).
#
# oarepo-requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""UI views for requests module."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, ClassVar

import marshmallow as ma
from flask import Blueprint, current_app, g, render_template
from flask_login import current_user, login_required
from flask_resources import route
from invenio_app_rdm.records_ui.views.deposits import (
    get_user_communities_memberships,
    load_custom_fields,
)
from invenio_app_rdm.requests_ui.views.requests import (
    _resolve_record_or_draft_files,
    _resolve_record_or_draft_media_files,
)
from invenio_checks.api import ChecksAPI
from invenio_drafts_resources.services import RecordService as DraftRecordService
from invenio_i18n.ext import current_i18n
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.requests import CommunityInclusion  # type: ignore[attr-defined]
from invenio_rdm_records.resources.serializers import UIJSONSerializer  # type: ignore[attr-defined]
from invenio_rdm_records.services.errors import RecordDeletedException  # type: ignore[attr-defined]
from invenio_records_resources.services import RecordService
from invenio_requests import current_request_type_registry
from invenio_requests.customizations import AcceptAction
from invenio_requests.views.decorators import pass_request
from invenio_users_resources.proxies import current_user_resources
from invenio_vocabularies.proxies import current_service as vocabulary_service
from marshmallow_utils.fields.babel import gettext_from_dict
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources import AllowedHtmlTagsComponent
from oarepo_ui.resources.base import UIComponentsResource
from oarepo_ui.resources.decorators import pass_route_args
from oarepo_ui.resources.form_config import FormConfigResourceConfig
from oarepo_ui.templating.data import FieldData
from sqlalchemy.orm.exc import NoResultFound  # type: ignore[attr-defined]

from oarepo_requests.ui.components import (
    ActionLabelsComponent,
    FormConfigCustomFieldsComponent,
    FormConfigRequestTypePropertiesComponent,
    RequestsUIConfigComponent,
)
from oarepo_requests.utils import (
    get_matching_service_for_refdict,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from flask import Flask
    from flask.typing import ResponseReturnValue
    from invenio_requests.customizations.request_types import RequestType


def _has_record_topic(request: Mapping[str, Any]) -> bool:
    """Check if request topic is a record (not user, community, etc.) using oarepo resolver."""
    topic = request["topic"]
    if not topic:
        return False
    try:
        service = get_matching_service_for_refdict(topic)
        return service is not None and isinstance(service, RecordService)
    except Exception:  # noqa: BLE001
        return False


def _resolve_topic_record_oarepo(request: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve topic record using oarepo utilities (model-agnostic version)."""
    topic_ref = request["topic"]
    if not topic_ref:  # pragma: no cover
        return {
            "permissions": {},
            "record_ui": None,
            "record": None,
            "model": None,
            "d": None,
            "record_detail_template": None,
        }
    try:
        service = get_matching_service_for_refdict(topic_ref)
        if not service:
            return {
                "record_ui": None,
                "record": None,
                "model": None,
                "d": None,
                "record_detail_template": None,
            }

        # Get record ID from reference dict
        pid = next(iter(topic_ref.values()))
        # Get entity type (e.g., "datasets")
        entity_type = next(iter(topic_ref.keys()))

        record = None

        # Try to read draft first if service supports drafts
        if isinstance(service, DraftRecordService):  # pragma: no cover
            with contextlib.suppress(NoResultFound, PIDDoesNotExistError, RecordDeletedException):
                record = service.read_draft(g.identity, pid, expand=True)

        # If no draft or not a draft service, try published record
        if not record:  # pragma: no cover
            try:
                record = service.read(g.identity, pid, expand=True)
            except (NoResultFound, RecordDeletedException):
                return {
                    "record_ui": None,
                    "record": None,
                    "model": None,
                    "d": None,
                    "record_detail_template": None,
                }

        if record:
            record_ui = UIJSONSerializer().dump_obj(record.to_dict())

            # Get model and ui_model from service config
            model = None
            ui_model: Mapping[str, Any] = {}
            if hasattr(service.config, "model") and service.config.model:
                model = service.config.model
                ui_model = getattr(model, "ui_model", {})

            # Create FieldData for template
            d = FieldData.create(
                api_data=record.to_dict() if record else {},
                ui_data=record_ui,
                ui_definitions=ui_model,
            )

            record_detail_template = f"{entity_type}/record_detail/main.html"

            return {
                "record_ui": record_ui,
                "record": record,
                "model": ui_model,
                "d": d,
                "record_detail_template": record_detail_template,
            }

    except Exception:  # noqa: BLE001, S110
        pass

    return {
        "record_ui": None,
        "record": None,
        "model": None,
        "d": None,
        "record_detail_template": None,
    }


@login_required
@pass_request(expand=True)
def user_dashboard_request_view(
    request: Any,
    **kwargs: Any,  # noqa: ARG001
) -> ResponseReturnValue:
    """User dashboard request details view."""
    avatar = current_user_resources.users_service.links_item_tpl.expand(g.identity, current_user)["avatar"]

    request_type = request["type"]
    request_is_accepted = request["status"] == AcceptAction.status_to

    has_topic = request["topic"] is not None
    has_record_topic = _has_record_topic(request)
    has_community_topic = has_topic and "community" in request["topic"]
    is_record_inclusion = request_type == CommunityInclusion.type_id
    # TODO: not possible to statically check permissions (create_comment) on our permissions policy i.e. it requires
    # event_type
    request_permissions = request.has_permissions_to(
        [
            "action_accept",
            "lock_request",
        ]
    )

    if has_record_topic:
        topic = _resolve_topic_record_oarepo(request)
        record_ui = topic["record_ui"]
        record = topic["record"]
        is_draft = record_ui["is_draft"] if record_ui else False
        is_published = record_ui["is_published"] if record_ui else False
        has_draft = record._record.has_draft if record else False  # NOQA: SLF001

        files = _resolve_record_or_draft_files(record_ui, request)
        media_files = _resolve_record_or_draft_media_files(record_ui, request)

        checks = None
        if current_app.config.get("CHECKS_ENABLED", False) and record:  # pragma: no cover
            if is_record_inclusion and has_draft:
                checks = ChecksAPI.get_runs(
                    record._record,  # noqa: SLF001
                    is_draft=True,
                )
            else:
                checks = ChecksAPI.get_runs(record._record)  # NOQA: SLF001

        if request_type == "record-deletion":  # pragma: no cover
            reason_title = vocabulary_service.read(
                g.identity,
                ("removalreasons", request["payload"]["reason"]),  # type: ignore[arg-type]
            ).to_dict()
            request["payload"]["reason_label"] = gettext_from_dict(
                reason_title["title"],
                current_i18n.locale,
                current_app.config.get("BABEL_DEFAULT_LOCALE", "en"),
            )

        return current_oarepo_ui.catalog.render_first_existing(
            [
                f"invenio_requests.{request_type}.index",
                "invenio_requests.details.index",
            ],
            user_avatar=avatar,
            invenio_request=request.to_dict(),
            record_ui=record_ui,
            record=record,
            checks=checks,
            permissions={**request_permissions},
            is_preview=is_draft,  # preview only when draft
            is_draft=is_draft,
            is_published=is_published,
            has_draft=has_draft,
            request_is_accepted=request_is_accepted,
            files=files,
            media_files=media_files,
            is_user_dashboard=True,
            custom_fields_ui=load_custom_fields()["ui"],
            user_communities_memberships=get_user_communities_memberships(),
            include_deleted=False,
            # OARepo specific for dynamic record templates
            d=topic.get("d"),
            model=topic.get("model"),
            record_detail_template=topic.get("record_detail_template"),
        )

    if has_community_topic or not has_topic:  # pragma: no cover
        return render_template(
            f"invenio_requests/{request_type}/user_dashboard.html",
            base_template="invenio_app_rdm/users/base.html",
            user_avatar=avatar,
            invenio_request=request.to_dict(),
            request_is_accepted=request_is_accepted,
            permissions={**request_permissions},
            include_deleted=False,
        )

    topic = _resolve_topic_record_oarepo(request)

    return render_template(
        [
            f"invenio_requests/{request_type}/index.html",
            "invenio_requests/details/index.html",
        ],
        base_template="invenio_app_rdm/users/base.html",
        user_avatar=avatar,
        record=None,
        record_ui=None,
        permissions={**topic["permissions"], **request_permissions},
        invenio_request=request.to_dict(),
        request_is_accepted=request_is_accepted,
        include_deleted=False,
    )


def create_requests_ui_blueprint(app: Flask) -> Blueprint:
    """Create the requests UI blueprint."""
    routes = app.config["RDM_REQUESTS_ROUTES"]
    blueprint = Blueprint(
        "invenio_app_rdm_requests",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    blueprint.add_url_rule(
        routes["user-dashboard-request-details"],
        view_func=user_dashboard_request_view,
    )
    return blueprint


class FormConfigResource(UIComponentsResource[FormConfigResourceConfig]):
    """A resource for form configuration."""

    def create_url_rules(self) -> list[dict[str, Any]]:
        """Create the URL rules for the record resource."""
        routes = []
        route_config = self.config.routes
        for route_name, route_url in route_config.items():
            routes.append(route("GET", route_url, getattr(self, route_name)))
        return routes

    def _get_form_config(self, **kwargs: Any) -> dict[str, Any]:
        """Get the form configuration for React forms.

        :param kwargs: Additional configuration options.
        :return: Dictionary with form configuration.
        """
        return self.config.form_config(**kwargs)  # type: ignore[no-any-return]

    @pass_route_args("request_type")
    def form_config(self, **kwargs: Any) -> dict[str, Any]:
        """Return form configuration.

        This is a view method that retrieves the form configuration by running
        the necessary components.
        """
        form_config = self._get_form_config()
        self.run_components("form_config", form_config=form_config, identity=g.identity, **kwargs)
        return form_config


class RequestTypeSchema(ma.fields.Str):
    """Schema that makes sure that the request type is a valid request type."""

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> RequestType:
        """Deserialize the value and check if it is a valid request type."""
        ret = super()._deserialize(value, attr, data, **kwargs)
        return current_request_type_registry.lookup(ret, quiet=True)


class RequestsFormConfigResourceConfig(FormConfigResourceConfig):
    """Config for the requests form config resource."""

    url_prefix = "/requests"
    blueprint_name = "oarepo_requests_form_config"
    components: ClassVar[list] = [
        AllowedHtmlTagsComponent,
        FormConfigCustomFieldsComponent,
        FormConfigRequestTypePropertiesComponent,
        ActionLabelsComponent,
        RequestsUIConfigComponent,
    ]
    request_request_type_args: ClassVar[dict] = {"request_type": RequestTypeSchema()}
    routes: Mapping[str, str] = {
        "form_config": "/configs/<request_type>",
    }


def create_requests_form_config_blueprint(app: Flask) -> Blueprint:  # NOQA: ARG001
    """Register blueprint for form config resource."""
    return FormConfigResource(RequestsFormConfigResourceConfig()).as_blueprint()  # type: ignore[arg-type]
