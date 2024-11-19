"""Proxy objects for accessing the current application's requests service and resource."""

from flask import current_app
from werkzeug.local import LocalProxy

current_oarepo_requests = LocalProxy(lambda: current_app.extensions["oarepo-requests"])
current_oarepo_requests_service = LocalProxy(
    lambda: current_app.extensions["oarepo-requests"].requests_service
)
current_oarepo_requests_resource = LocalProxy(
    lambda: current_app.extensions["oarepo-requests"].requests_resource
)
