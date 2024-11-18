from invenio_requests.records.api import Request
from invenio_requests.services import RequestsServiceConfig
from invenio_requests.services.requests import RequestLink

from oarepo_requests.resolvers.ui import resolve


class RequestEntityLink(RequestLink):
    def __init__(self, uritemplate, when=None, vars=None, entity="topic"):
        super().__init__(uritemplate, when, vars)
        self._entity = entity

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
        reference_dict = getattr(obj, self._entity).reference_dict
        key = "entity:" + ":".join(
            f"{x[0]}:{x[1]}" for x in sorted(reference_dict.items())
        )
        if key in ctx:
            return ctx[key]
        try:
            entity = resolve(ctx["identity"], reference_dict, keep_all_links=True)
        except Exception:  # noqa
            entity = {}
        ctx[key] = entity
        return entity

    def _expand_entity(self, entity, vars):
        if "links" in entity:
            vars.update({f"entity_{k}": v for k, v in entity["links"].items()})

    def expand(self, obj, context):
        """Expand the URI Template."""
        # Optimization: pre-resolve the entity and put it into the shared context
        # under the key - so that it can be reused by other links
        self._resolve(obj, context)
        return super().expand(obj, context)


class RequestEntityLinks(RequestEntityLink):
    """Utility class for keeping track of and resolve links."""

    def __init__(self, *request_entity_links, entity="topic", when=None, vars=None):
        """Constructor."""
        self._request_entity_links = [
            {name: RequestEntityLink(link, entity=entity, **kwargs)}
            for name, link, kwargs in request_entity_links
        ]
        self._entity = entity
        self._when_func = when
        self._vars_func = vars

    def expand(self, obj, context):
        res = {}
        for link_dict in self._request_entity_links:
            name = list(link_dict.keys())[0]
            link = list(link_dict.values())[0]
            if link.should_render(obj, context):
                res[name] = link.expand(obj, context)
        if hasattr(obj.type, "extra_request_links"):
            entity = self._resolve(obj, context)
            res.update(
                obj.type.extra_request_links(
                    request=obj,
                    **(context | {"cur_entity": entity, "entity_type": self._entity}),
                )
            )
        return res


class OARepoRequestsServiceConfig(RequestsServiceConfig):
    service_id = "oarepo_requests"

    links_item = {
        "self": RequestLink("{+api}/requests/extended/{id}"),
        "comments": RequestLink("{+api}/requests/extended/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/extended/{id}/timeline"),
        "self_html": RequestLink("{+ui}/requests/{id}"),
        "topic": RequestEntityLinks(
            ("self", "{+entity_self}", {}),  # can't use self=RequestEntityLink...
            ("self_html", "{+entity_self_html}", {}),
        ),
        "created_by": RequestEntityLinks(
            ("self", "{+entity_self}", {}),
            ("self_html", "{+entity_self_html}", {}),
            entity="created_by",
        ),
        "receiver": RequestEntityLinks(
            ("self", "{+entity_self}", {}),
            ("self_html", "{+entity_self_html}", {}),
            entity="receiver",
        ),
    }
