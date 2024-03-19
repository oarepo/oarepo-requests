from flask_resources import route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_requests.resources.events.resource import RequestCommentsResource

class OARepoRequestsCommentsResource(RequestCommentsResource, ErrorHandlersMixin):

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        base_routes = super().create_url_rules()
        routes = self.config.routes

        url_rules = [
            route("POST", routes["list-extended"], self.create_extended),
            route("GET", routes["item-extended"], self.read_extended),
            route("PUT", routes["item-extended"], self.update_extended),
            route("DELETE", routes["item-extended"], self.delete_extended),
            route("GET", routes["timeline-extended"], self.search_extended),
        ]
        return url_rules + base_routes

    # from parent
    def create_extended(self):
        return super().create()

    def read_extended(self):
        return super().read()

    def update_extended(self):
        return super().update()

    def delete_extended(self):
        return super().delete()

    def search_extended(self):
        return super().search()