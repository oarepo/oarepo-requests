from functools import cached_property

from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.services.records.params import FilterParam
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

from oarepo_requests.resources.ui import OARepoRequestsUIJSONSerializer


class RequestOwnerFilterParam(FilterParam):
    def apply(self, identity, search, params):
        value = params.pop(self.param_name, None)
        if value is not None:
            search = search.filter("term", **{self.field_name: identity.id})
        return search


class RequestReceiverFilterParam(FilterParam):
    def apply(self, identity, search, params):
        value = params.pop(self.param_name, None)
        my_groups = [n.value for n in identity.provides if n.method == "role"]
        if value is not None:
            search = search.filter(
                Bool(
                    should=[
                        # explicitly myself
                        Term(**{f"{self.field_name}.user": identity.id}),
                        # my roles
                        *[
                            Term(**{f"{self.field_name}.group": group_id})
                            for group_id in my_groups
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

        class LazySerializer:
            @cached_property
            def __instance(self):
                return OARepoRequestsUIJSONSerializer()

            @property
            def serialize_object_list(self):
                return self.__instance.serialize_object_list

            @property
            def serialize_object(self):
                return self.__instance.serialize_object

        RequestsResourceConfig.response_handlers = {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(LazySerializer()),
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
        status._label = _("Status")

        # add extra request types dynamically
        type._value_labels = {
            rt.type_id: rt.name for rt in iter(current_request_type_registry)
        }
        type._label = _("Type")
