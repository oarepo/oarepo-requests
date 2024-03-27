def create_oarepo_requests(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.requests_resource.as_blueprint()

    from oarepo_requests.services.search_options import override_invenio_request_search_options
    blueprint.record_once(override_invenio_request_search_options)

    return blueprint


def create_oarepo_requests_events(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.request_events_resource.as_blueprint()
    return blueprint
