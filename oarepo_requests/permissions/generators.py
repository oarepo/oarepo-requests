from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl
from oarepo_requests.permissions.identity import request_active


class RequestActive(Generator):

    def needs(self, **kwargs):
        return [request_active]

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as system process."""
        if request_active in identity.provides:
            return dsl.Q("match_all")
        else:
            return []

class SubmissionReviewer(Generator):
    # todo - from rdm, here should be generator for accesing request topic by receivers

    def needs(self, record=None, **kwargs):
        """Set of Needs granting permission."""
        if record is None or record.parent.review is None:
            return []

        # we only expect submission review requests here
        # and as such, we expect the receiver to be a community
        # and the topic to be a record
        request = record.parent.review
        receiver = request.receiver
        if receiver is not None:
            return receiver.get_needs(ctx=request.type.needs_context)
        return []