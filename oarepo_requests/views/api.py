def create_oarepo_requests(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    return ext.requests_resource.as_blueprint()