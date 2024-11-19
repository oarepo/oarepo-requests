#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Resource for request events/comments that lives on the extended url."""

from flask_resources import route
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_requests.resources.events.resource import RequestCommentsResource


class OARepoRequestsCommentsResource(RequestCommentsResource, ErrorHandlersMixin):
    """OARepo extensions to invenio requests comments resource."""

    def create_url_rules(self) -> list[dict]:
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
    def create_extended(self) -> tuple[dict, int]:
        """Create a new comment."""
        return super().create()

    def read_extended(self) -> tuple[dict, int]:
        """Read a comment."""
        return super().read()

    def update_extended(self) -> tuple[dict, int]:
        """Update a comment."""
        return super().update()

    def delete_extended(self) -> tuple[dict, int]:
        """Delete a comment."""
        return super().delete()

    def search_extended(self) -> tuple[dict, int]:
        """Search for comments."""
        return super().search()
