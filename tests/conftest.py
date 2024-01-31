import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_access.permissions import system_identity
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.proxies import current_request_type_registry, current_requests
from invenio_requests.records.api import Request, RequestEventFormat
from thesis.records.api import ThesisDraft, ThesisRecord

from oarepo_requests.resolvers.ui import (
    draft_record_entity_reference_ui_resolver,
    user_entity_reference_ui_resolver,
)


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def urls():
    return {"BASE_URL": "/thesis/", "BASE_URL_REQUESTS": "/requests/"}


@pytest.fixture()
def publish_request_data_function():
    def ret_data(receiver_id, record_id):
        return {
            "receiver": {"user": receiver_id},
            "request_type": "publish_draft",
            "topic": {"thesis_draft": record_id},
        }

    return ret_data


@pytest.fixture()
def delete_record_data_function():
    def ret_data(receiver_id, record_id):
        return {
            "receiver": {"user": receiver_id},
            "request_type": "delete_record",
            "topic": {"thesis": record_id},
        }

    return ret_data


@pytest.fixture()
def serialization_result():
    def _result(topic_id, request_id):
        return {
            "id": request_id,  #'created': '2024-01-29T22:09:13.931722',
            #'updated': '2024-01-29T22:09:13.954850',
            "links": {
                "actions": {
                    "accept": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/accept"
                },
                "self": f"https://127.0.0.1:5000/api/requests/extended/{request_id}",
                "comments": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/comments",
                "timeline": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/timeline",
            },
            "revision_id": 3,
            "type": "publish_draft",
            "title": "",
            "number": "1",
            "status": "submitted",
            "is_closed": False,
            "is_open": True,
            "expires_at": None,
            "is_expired": False,
            "created_by": {"user": "1"},
            "receiver": {"user": "2"},
            "topic": {"thesis_draft": topic_id},
        }

    return _result


@pytest.fixture()
def ui_serialization_result():
    # TODO correct time formats, translations etc
    def _result(topic_id, request_id):
        return {
            # 'created': '2024-01-26T10:06:17.945916',
            "created_by": {
                "label": "id: 1",
                "reference": {"user": "1"},
                "type": "user",
            },
            "description": "request publishing of a draft",
            "expires_at": None,
            "id": request_id,
            "is_closed": False,
            "is_expired": False,
            "is_open": True,
            "links": {
                "actions": {
                    "accept": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/accept"
                },
                "self": f"https://127.0.0.1:5000/api/requests/extended/{request_id}",
                "comments": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/comments",
                "timeline": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/timeline",
            },
            "number": "1",
            "receiver": {
                "label": "user2@example.org",
                "link": "https://127.0.0.1:5000/api/users/2",
                "reference": {"user": "2"},
                "type": "user",
            },
            "revision_id": 3,
            "status": "Submitted",
            "title": "",
            "topic": {
                "label": "",
                "link": f"https://127.0.0.1:5000/api/thesis/{topic_id}/draft",
                "reference": {"thesis_draft": topic_id},
                "type": "thesis_draft",
            },
            "type": "publish_draft",
            # 'updated': '2024-01-26T10:06:18.084317'
        }

    return _result


@pytest.fixture(scope="module")
def app_config(app_config):
    app_config["REQUESTS_REGISTERED_EVENT_TYPES"] = [LogEventType(), CommentEventType()]
    app_config["SEARCH_HOSTS"] = [
        {
            "host": os.environ.get("OPENSEARCH_HOST", "localhost"),
            "port": os.environ.get("OPENSEARCH_PORT", "9200"),
        }
    ]
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config["CACHE_TYPE"] = "SimpleCache"

    app_config["ENTITY_REFERENCE_UI_RESOLVERS"] = {
        "user": user_entity_reference_ui_resolver,
        "thesis_draft": draft_record_entity_reference_ui_resolver,
    }

    return app_config


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def identity_simple_2():
    """Simple identity fixture."""
    i = Identity(2)
    i.provides.add(UserNeed(2))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def requests_service(app):
    """Request Factory fixture."""

    return current_requests.requests_service


@pytest.fixture(scope="module")
def request_events_service(app):
    """Request Factory fixture."""
    service = current_requests.request_events_service
    return service


@pytest.fixture()
def create_request(requests_service):
    """Request Factory fixture."""

    def _create_request(identity, input_data, receiver, request_type, **kwargs):
        """Create a request."""
        # Need to use the service to get the id
        item = requests_service.create(
            identity, input_data, request_type=request_type, receiver=receiver, **kwargs
        )
        return item._request

    return _create_request


@pytest.fixture
def request_data_factory():
    def create_data(community, topic, data):
        if not isinstance(community, str):
            community_id = community.id
        else:
            community_id = community
        input_data = {
            "receiver": {"oarepo_community": community_id},
            "request_type": type,
            "topic": {"thesis": topic["id"]},
        }
        if creator:
            input_data["creator"] = creator
        if payload:
            input_data["payload"] = payload
        return input_data

    return create_data


@pytest.fixture()
def submit_request(create_request, requests_service, **kwargs):
    """Opened Request Factory fixture."""

    def _submit_request(identity, data, **kwargs):
        """Create and submit a request."""
        request = create_request(identity, input_data=data, **kwargs)
        id_ = request.id
        return requests_service.execute_action(identity, id_, "submit", data)._request

    return _submit_request


@pytest.fixture()
def users(app, db):
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="user1@example.org",
            password="password",
            active=True,
        )
        user2 = datastore.create_user(
            email="user2@example.org",
            password="beetlesmasher",
            active=True,
        )

    db.session.commit()
    return [user1, user2]

    """
    from invenio_db import db

    user1 = UserFixture(
        email="user1@example.org",
        password="password",
        preferences={"visibility": "public"},
    )
    user1.create(app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password="password",
        preferences={"visibility": "public"},
    )
    user2.create(app, db)
    
    return [user1, user2]
    """


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    login_user(user)
    login_user_via_session(client, email=user.email)
    return client


@pytest.fixture()
def client_logged_as(client, users):
    """Logs in a user to the client."""

    def log_user(user_email):
        """Log the user."""
        available_users = users

        user = next((u for u in available_users if u.email == user_email), None)
        login_user(user, remember=True)
        login_user_via_session(client, email=user_email)
        return client

    return log_user


@pytest.fixture()
def logged_client_post(client_logged_as):
    def _logged_client_post(user, method, *args, **kwargs):
        applied_client = client_logged_as(user.email)
        return getattr(applied_client, method)(*args, **kwargs)

    return _logged_client_post


@pytest.fixture()
def logged_clients(users, client_logged_as):
    return [client_logged_as(user.email) for user in users]


@pytest.fixture
def client_factory(app):
    def _client_factory():
        with app.test_client() as client:
            return client

    return _client_factory


@pytest.fixture(scope="function")
def request_record_input_data():
    """Input data to a Request record."""
    ret = {
        "title": "Doc1 approval",
        "payload": {
            "content": "Can you approve my document doc1 please?",
            "format": RequestEventFormat.HTML.value,
        },
    }
    return ret


@pytest.fixture(scope="module")
def record_service():
    return current_service


@pytest.fixture()
def example_topic_draft(record_service, identity_simple):
    draft = record_service.create(identity_simple, {})
    return draft._obj


@pytest.fixture()
def example_draft_service_bypass(app, db):
    record = ThesisDraft.create({})
    db.session.commit()
    return record


@pytest.fixture()
def record_factory(record_service):
    def record():
        draft = record_service.create(system_identity, {})
        record = record_service.publish(system_identity, draft.id)
        return record._obj

    return record


@pytest.fixture(scope="function")
def example_topic(record_service, identity_simple):
    draft = record_service.create(identity_simple, {})
    record = record_service.publish(identity_simple, draft.id)
    id_ = record.id
    record = ThesisRecord.pid.resolve(id_)
    return record


@pytest.fixture(scope="module")
def identity_creator(identity_simple):  # for readability
    return identity_simple


@pytest.fixture(scope="module")
def identity_receiver(identity_simple_2):  # for readability
    return identity_simple_2


@pytest.fixture(scope="function")
def request_with_receiver_user(
    requests_service, example_topic, identity_creator, users
):
    receiver = users[1]
    type_ = current_request_type_registry.lookup("generic_request", quiet=True)
    request_item = requests_service.create(
        identity_creator, {}, type_, receiver=receiver, topic=example_topic
    )
    request = Request.get_record(request_item.id)
    return request_item


# -------
import os

import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from thesis.proxies import current_service


@pytest.fixture
def request_data(example_topic):
    input_data = {
        "receiver": {"user": "1"},
        "request_type": "generic_request",
        "topic": {"thesis": example_topic["id"]},
    }
    return input_data


@pytest.fixture()
def client_with_credentials(client, users):
    """Log in a user to the client."""
    user = users[2]
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)

    return client
