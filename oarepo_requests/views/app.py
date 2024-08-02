from flask import Blueprint


def create_app_blueprint(app):
    blueprint = Blueprint("oarepo_requests_app", __name__, url_prefix="/requests/")
    blueprint.record_once(register_autoapprove_entity_resolver)
    return blueprint


def register_autoapprove_entity_resolver(state):
    from oarepo_requests.resolvers.autoapprove import AutoApproveResolver

    app = state.app
    requests = app.extensions["invenio-requests"]
    requests.entity_resolvers_registry.register_type(AutoApproveResolver())


def create_app_events_blueprint(app):
    blueprint = Blueprint(
        "oarepo_requests_events_app", __name__, url_prefix="/requests/"
    )
    return blueprint
