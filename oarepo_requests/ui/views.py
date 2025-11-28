from flask import Blueprint, Flask


def create_blueprint(app: Flask) -> Blueprint:
    """Create a blueprint for the requests endpoint.

    :param app: Flask application
    """
    blueprint = Blueprint(
        "oarepo_requests",
        __name__,
        template_folder="templates",
    )
    return blueprint
