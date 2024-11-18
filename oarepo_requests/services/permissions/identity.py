"""Request needs."""

from invenio_access.permissions import SystemRoleNeed

request_active = SystemRoleNeed("request")
"""Need that is added to identity whenever a request is being handled (inside the 'accept' action)."""
