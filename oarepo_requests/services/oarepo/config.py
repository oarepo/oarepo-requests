from invenio_requests.records.api import Request
from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink

from oarepo_requests.resolvers.ui import resolve


class RequestEntityLink(RequestLink):
    def __init__(self, uritemplate, when=None, vars=None, entity="topic"):
        super().__init__(uritemplate, when, vars)
        self.entity = entity

    def vars(self, record: Request, vars):
        super().vars(record, vars)
        entity = self._resolve(record, vars)
        self._expand_entity(entity, vars)
        return vars

    def should_render(self, obj, ctx):
        if not super().should_render(obj, ctx):
            return False
        if self.expand(obj, ctx):
            return True

    def _resolve(self, obj, ctx):
        reference_dict = getattr(obj, self.entity).reference_dict
        key = "entity:" + ":".join(
            f"{x[0]}:{x[1]}" for x in sorted(reference_dict.items())
        )
        if key in ctx:
            return ctx[key]
        try:
            entity = resolve(ctx["identity"], reference_dict)
        except Exception:  # noqa
            entity = {}
        ctx[key] = entity
        return entity

    def _expand_entity(self, entity, vars):
        vars.update({f"entity_{k}": v for k, v in entity.get("links", {}).items()})


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    service_id = "oarepo_requests"

    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
        "self_html": RequestLink("{+ui}/requests/{id}"),
        "topic": RequestEntityLink("{+entity_self}"),
        "topic_html": RequestEntityLink("{+entity_self_html}"),
        "created_by": RequestEntityLink("{+entity_self}", entity="created_by"),
        "created_by_html": RequestEntityLink(
            "{+entity_self_html}", entity="created_by"
        ),
        "receiver": RequestEntityLink("{+entity_self}", entity="receiver"),
        "receiver_html": RequestEntityLink("{+entity_self_html}", entity="receiver"),
    }
