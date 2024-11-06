from flask import g
from flask_resources import resource_requestctx, route
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.resources.records.resource import (
    request_read_args,
    request_view_args,
)
from invenio_records_resources.services import LinksTemplate
from oarepo_ui.proxies import current_oarepo_ui
from oarepo_ui.resources.resource import UIResource
from oarepo_ui.resources.templating.data import FieldData

from oarepo_requests.ui.config import RequestUIResourceConfig


def make_links_absolute(links, api_prefix):
    # make links absolute
    for k, v in list(links.items()):
        if not isinstance(v, str):
            continue
        if not v.startswith("/") and not v.startswith("https://"):
            v = f"/api{api_prefix}{v}"
            links[k] = v


class RequestUIResource(UIResource):
    config: RequestUIResourceConfig

    @property
    def api_service(self):
        return current_service_registry.get(self.config.api_service)

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = []
        route_config = self.config.routes
        for route_name, route_url in route_config.items():
            routes.append(route("GET", route_url, getattr(self, route_name)))
        return routes

    def expand_detail_links(self, identity, record):
        """Get links for this result item."""
        tpl = LinksTemplate(
            self.config.ui_links_item, {"url_prefix": self.config.url_prefix}
        )
        return tpl.expand(identity, record)

    def _get_custom_fields(self, **kwargs):
        return self.config.custom_fields(identity=g.identity, **kwargs)

    @request_read_args
    @request_view_args
    def detail(self):
        """Returns item detail page."""
        api_record = self.api_service.read(
            g.identity, resource_requestctx.view_args["pid_value"]
        )
        render_method = self.get_jinjax_macro(
            "detail",
            identity=g.identity,
            args=resource_requestctx.args,
            view_args=resource_requestctx.view_args,
        )

        # TODO: handle permissions UI way - better response than generic error
        record = self.config.ui_serializer.dump_obj(api_record.to_dict())
        record.setdefault("links", {})

        ui_links = self.expand_detail_links(identity=g.identity, record=api_record)

        record["links"].update(
            {
                "ui_links": ui_links,
            }
        )

        make_links_absolute(record["links"], self.config.url_prefix)

        extra_context = dict()
        # TODO: this needs to be reimplemented in:
        # https://linear.app/ducesnet/issue/BE-346/on-request-detail-page-generate-form-config-for-the-comment-stream
        form_config = {}

        self.run_components(
            "form_config",
            api_record=api_record,
            record=record,
            identity=g.identity,
            form_config=form_config,
            extra_context=extra_context,
            args=resource_requestctx.args,
            view_args=resource_requestctx.view_args,
            ui_links=ui_links,
        )

        self.run_components(
            "before_ui_detail",
            api_record=api_record,
            record=record,
            identity=g.identity,
            extra_context=extra_context,
            args=resource_requestctx.args,
            view_args=resource_requestctx.view_args,
            ui_links=ui_links,
            custom_fields=self._get_custom_fields(
                api_record=api_record, resource_requestctx=resource_requestctx
            ),
        )

        metadata = dict(record.get("metadata", record))
        render_kwargs = {
            **extra_context,
            "extra_context": extra_context,  # for backward compatibility
            "metadata": metadata,
            "ui": dict(record.get("ui", record)),
            "record": record,
            "form_config": form_config,
            "api_record": api_record,
            "ui_links": ui_links,
            "context": current_oarepo_ui.catalog.jinja_env.globals,
            "d": FieldData(record, self.ui_model),
        }

        return current_oarepo_ui.catalog.render(
            render_method,
            **render_kwargs,
        )

    @property
    def ui_model(self):
        return current_oarepo_ui.ui_models.get(
            self.config.api_service.replace("-", "_"), {}
        )

    def get_jinjax_macro(
        self,
        template_type,
        identity=None,
        args=None,
        view_args=None,
        default_macro=None,
    ):
        """
        Returns which jinjax macro (name of the macro, including optional namespace in the form of "namespace.Macro")
        should be used for rendering the template.
        """
        if default_macro:
            return self.config.templates.get(template_type, default_macro)
        return self.config.templates[template_type]

    def tombstone(self, error, *args, **kwargs):
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "tombstone",
                identity=g.identity,
                default_macro="Tombstone",
            ),
            pid=getattr(error, "pid_value", None) or getattr(error, "pid", None),
        )

    def not_found(self, error, *args, **kwargs):
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "not_found",
                identity=g.identity,
                default_macro="NotFound",
            ),
            pid=getattr(error, "pid_value", None) or getattr(error, "pid", None),
            error=error,
        )

    def permission_denied(self, error, *args, **kwargs):
        return current_oarepo_ui.catalog.render(
            self.get_jinjax_macro(
                "permission_denied",
                identity=g.identity,
                default_macro="PermissionDenied",
            ),
            pid=getattr(error, "pid_value", None) or getattr(error, "pid", None),
            error=error,
        )
