def create_oarepo_requests(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.requests_resource.as_blueprint()
    return blueprint
