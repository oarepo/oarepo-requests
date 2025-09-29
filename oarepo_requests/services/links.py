from invenio_records_resources.services.base.links import EndpointLink
from invenio_requests.resolvers.registry import ResolverRegistry


class RefEndpointLink(EndpointLink):
    def __init__(
        self, endpoint, when=None, vars=None, params=None, ref_querystring=None
    ):
        """Constructor.

        :param endpoint: str. endpoint of the URL
        :param when: fn(obj, dict) -> bool, when the URL should be rendered
        :param vars: fn(obj, dict), mutate dict in preparation for expansion
        :param params: list, parameters (excluding querystrings) used for expansion
        """
        super().__init__(endpoint, when, vars, params)
        self._ref_querystring = ref_querystring

    def expand(self, obj, context):
        """Expand the endpoint.

        Note: "args" key in generated values for expansion has special meaning.
              It is used for querystring parameters.
        """
        ret = super().expand(obj, context)
        topic_ref = ResolverRegistry.reference_entity(obj)
        return f"{ret}?{self._ref_querystring}={next(iter(topic_ref.keys()))}:{next(iter(topic_ref.values()))}"
