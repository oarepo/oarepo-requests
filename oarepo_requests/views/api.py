def create_oarepo_requests(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.requests_resource.as_blueprint()

    from oarepo_requests.invenio_patches import override_invenio_requests_config

    blueprint.record_once(override_invenio_requests_config)
    blueprint.record_once(register_autoapprove_entity_resolver)

    return blueprint


def register_autoapprove_entity_resolver(state):
    from oarepo_requests.resolvers.autoapprove import AutoApproveResolver

    app = state.app
    requests = app.extensions["invenio-requests"]
    requests.entity_resolvers_registry.register_type(AutoApproveResolver())


def create_oarepo_requests_events(app):
    """Create requests blueprint."""
    ext = app.extensions["oarepo-requests"]
    blueprint = ext.request_events_resource.as_blueprint()
    return blueprint
