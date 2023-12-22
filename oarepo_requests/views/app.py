from flask import Blueprint


def create_app_blueprint(app):
    blueprint = Blueprint(
        "oarepo_requests_app", __name__, url_prefix="/requests"
    )
    return blueprint