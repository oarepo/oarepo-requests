from functools import cached_property

from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.records.params import FilterParam
from invenio_requests.resources.events.config import RequestCommentsResourceConfig
from invenio_requests.resources.requests.config import (
    RequestSearchRequestArgsSchema,
    RequestsResourceConfig,
)
from invenio_requests.services.requests.config import (
    RequestSearchOptions,
    RequestsServiceConfig,
)
from marshmallow import fields
from opensearch_dsl.query import Bool, Term

from oarepo_requests.resources.ui import (
    OARepoRequestEventsUIJSONSerializer,
    OARepoRequestsUIJSONSerializer,
)
from oarepo_requests.services.oarepo.config import OARepoRequestsServiceConfig


class RequestOwnerFilterParam(FilterParam):
    def apply(self, identity, search, params):
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter("term", **{self.field_name: identity.id})
        return search


class RequestReceiverFilterParam(FilterParam):
    def apply(self, identity, search, params):
        value = params.pop(self.param_name, None)
        my_roles = [n.value for n in identity.provides if n.method == "role"]
        if value is not None:
            search = search.filter(
                Bool(
                    should=[
                        # explicitly myself
                        Term(**{f"{self.field_name}.user": identity.id}),
                        # my roles
                        *[
                            Term(**{f"{self.field_name}.group": role_id})
                            for role_id in my_roles
                        ],
                        # TODO: add my communities where I have a role to accept requests
                    ],
                    minimum_should_match=1,
                )
            )
        return search


class EnhancedRequestSearchOptions(RequestSearchOptions):
    params_interpreters_cls = RequestSearchOptions.params_interpreters_cls + [
        RequestOwnerFilterParam.factory("mine", "created_by.user"),
        RequestReceiverFilterParam.factory("assigned", "receiver"),
    ]


class ExtendedRequestSearchRequestArgsSchema(RequestSearchRequestArgsSchema):
    mine = fields.Boolean()
    assigned = fields.Boolean()


def override_invenio_requests_config(blueprint, *args, **kwargs):
    with blueprint.app.app_context():
        # this monkey patch should be done better (support from invenio)
        RequestsServiceConfig.search = EnhancedRequestSearchOptions
        RequestsResourceConfig.request_search_args = (
            ExtendedRequestSearchRequestArgsSchema
        )
        # add extra links to the requests
        for k, v in OARepoRequestsServiceConfig.links_item.items():
            if k not in RequestsServiceConfig.links_item:
                RequestsServiceConfig.links_item[k] = v

        class LazySerializer:
            def __init__(self, serializer_cls):
                self.serializer_cls = serializer_cls

            @cached_property
            def __instance(self):
                return self.serializer_cls()

            @property
            def serialize_object_list(self):
                return self.__instance.serialize_object_list

            @property
            def serialize_object(self):
                return self.__instance.serialize_object

        RequestsResourceConfig.response_handlers = {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                LazySerializer(OARepoRequestsUIJSONSerializer), headers=etag_headers
            ),
        }

        RequestCommentsResourceConfig.response_handlers = {
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                LazySerializer(OARepoRequestEventsUIJSONSerializer),
                headers=etag_headers,
            ),
            **RequestCommentsResourceConfig.response_handlers,
        }

        from invenio_requests.proxies import current_request_type_registry
        from invenio_requests.services.requests.facets import status, type
        from oarepo_runtime.i18n import lazy_gettext as _

        status._value_labels = {
            "submitted": _("Submitted"),
            "expired": _("Expired"),
            "accepted": _("Accepted"),
            "declined": _("Declined"),
            "cancelled": _("Cancelled"),
        }
        status._label = _("Request status")

        # add extra request types dynamically
        type._value_labels = {
            rt.type_id: rt.name for rt in iter(current_request_type_registry)
        }
        type._label = _("Type")
