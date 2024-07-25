from flask_principal import Identity
from invenio_access.permissions import SystemRoleNeed

request_active = SystemRoleNeed("request")
