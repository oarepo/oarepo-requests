from invenio_access.permissions import system_identity
from invenio_notifications.services.generators import EntityResolve
from invenio_requests.records.api import Request


class RequestEntityResolve(EntityResolve):
    """Entity resolver that adds the correct title if it is missing."""

    def __call__(self, notification):
        notification = super().__call__(notification)
        request_dict = notification.context["request"]
        if request_dict.get("title"):
            return request_dict

        request = Request.get_record(request_dict["id"])
        request_dict["title"] = request.type.stateful_name(system_identity, topic=None)
        return notification
