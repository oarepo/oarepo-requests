import copy
import os

import pytest
from flask_principal import UserNeed
from flask_security import login_user
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from invenio_i18n import lazy_gettext as _
from invenio_records_permissions.generators import AnyUser, AuthenticatedUser, Generator
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.proxies import current_requests
from invenio_requests.records.api import RequestEventFormat
from invenio_users_resources.records import UserAggregate
from oarepo_runtime.services.permissions import RecordOwners
from oarepo_workflows import (
    AutoApprove,
    AutoRequest,
    IfInState,
    WorkflowRequest,
    WorkflowRequestPolicy,
    WorkflowTransitions,
)
from oarepo_workflows.base import Workflow
from oarepo_workflows.requests import RecipientGeneratorMixin
from thesis.proxies import current_service
from thesis.records.api import ThesisDraft

from oarepo_requests.actions.generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from oarepo_requests.receiver import default_workflow_receiver_function
from oarepo_requests.services.permissions.workflow_policies import (
    DefaultWithRequestsWorkflowPermissionPolicy,
)
from oarepo_requests.types import ModelRefTypes, NonDuplicableOARepoRequestType


class TestUserReceiver(RecipientGeneratorMixin, Generator):
    def needs(self, **kwargs):
        return [UserNeed(2)]

    def reference_receivers(self, **kwargs):
        return [{"user": "2"}]


class DefaultRequests(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[TestUserReceiver()],
        transitions=WorkflowTransitions(
            submitted="publishing", accepted="published", declined="draft"
        ),
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[TestUserReceiver()],
        transitions=WorkflowTransitions(
            submitted="deleting", accepted="deleted", declined="published"
        ),
    )
    edit_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
    )


class RequestsWithApprove(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("approved", [AutoRequest()])],
        recipients=[TestUserReceiver()],
        transitions=WorkflowTransitions(
            submitted="publishing", accepted="published", declined="approved"
        ),
    )
    approve_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[TestUserReceiver()],
        transitions=WorkflowTransitions(
            submitted="approving", accepted="approved", declined="draft"
        ),
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[TestUserReceiver()],
        transitions=WorkflowTransitions(
            submitted="deleting", accepted="deleted", declined="published"
        ),
    )
    edit_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
    )


class ApproveRequestType(NonDuplicableOARepoRequestType):
    type_id = "approve_draft"
    name = _("Approve draft")

    available_actions = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request approving of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class TestWorkflowPolicy(DefaultWithRequestsWorkflowPermissionPolicy):
    can_read = [
        IfInState("draft", [RecordOwners()]),
        IfInState("publishing", [RecordOwners(), TestUserReceiver()]),
        IfInState("published", [AnyUser()]),
        IfInState("deleting", [AnyUser()]),
    ]


class WithApprovalPermissionPolicy(DefaultWithRequestsWorkflowPermissionPolicy):
    can_read = [
        IfInState("draft", [RecordOwners()]),
        IfInState("approving", [RecordOwners(), TestUserReceiver()]),
        IfInState("approved", [RecordOwners(), TestUserReceiver()]),
        IfInState("publishing", [RecordOwners(), TestUserReceiver()]),
        IfInState("deleting", [AuthenticatedUser()]),
    ]


WORKFLOWS = {
    "default": Workflow(
        label=_("Default workflow"),
        permission_policy_cls=TestWorkflowPolicy,
        request_policy_cls=DefaultRequests,
    ),
    "with_approve": Workflow(
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissionPolicy,
        request_policy_cls=RequestsWithApprove,
    ),
}


@pytest.fixture
def change_workflow_function():
    from oarepo_workflows.proxies import current_oarepo_workflows

    return current_oarepo_workflows.set_workflow


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def vocab_cf(app, db, cache):
    from oarepo_runtime.services.custom_fields.mappings import prepare_cf_indices

    prepare_cf_indices()
    ThesisDraft.index.refresh()


@pytest.fixture()
def urls():
    return {"BASE_URL": "/thesis/", "BASE_URL_REQUESTS": "/requests/"}


@pytest.fixture()
def publish_request_data_function():
    def ret_data(record_id):
        return {
            "request_type": "publish_draft",
            "topic": {"thesis_draft": record_id},
        }

    return ret_data


@pytest.fixture()
def edit_record_data_function():
    def ret_data(record_id):
        return {
            "request_type": "edit_published_record",
            "topic": {"thesis": record_id},
        }

    return ret_data


@pytest.fixture()
def delete_record_data_function():
    def ret_data(record_id):
        return {
            "request_type": "delete_published_record",
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
                    "cancel": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/cancel"
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
                "label": "user1@example.org",
                "links": {"self": "https://127.0.0.1:5000/api/users/1"},
                "reference": {"user": "1"},
                "type": "user",
            },
            "description": "Request publishing of a draft",
            "expires_at": None,
            "id": request_id,
            "is_closed": False,
            "is_expired": False,
            "is_open": True,
            "links": {
                "actions": {
                    "cancel": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/cancel"
                },
                "self": f"https://127.0.0.1:5000/api/requests/extended/{request_id}",
                "comments": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/comments",
                "timeline": f"https://127.0.0.1:5000/api/requests/extended/{request_id}/timeline",
            },
            "number": "1",
            "receiver": {"label": "id: 2", "reference": {"user": "2"}, "type": "user"},
            "revision_id": 3,
            "status": "Submitted",
            "title": "",
            "topic": {
                "label": f"id: {topic_id}",
                "links": {
                    "self": f"https://127.0.0.1:5000/api/thesis/{topic_id}/draft",
                    "self_html": f"https://127.0.0.1:5000/thesis/{topic_id}/preview",
                },
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
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    app_config["CACHE_TYPE"] = "SimpleCache"

    app_config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = default_workflow_receiver_function

    app_config["WORKFLOWS"] = WORKFLOWS
    app_config["REQUESTS_REGISTERED_TYPES"] = [ApproveRequestType()]
    return app_config


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


@pytest.fixture()
def users(app, db, UserFixture):
    user1 = UserFixture(
        email="user1@example.org",
        password="password",
        active=True,
        confirmed=True,
    )
    user1.create(app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password="beetlesmasher",
        active=True,
        confirmed=True,
    )
    user2.create(app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password="beetlesmasher",
        active=True,
        confirmed=True,
    )
    user3.create(app, db)

    db.session.commit()
    UserAggregate.index.refresh()
    return [user1, user2, user3]


class LoggedClient:
    def __init__(self, client, user_fixture):
        self.client = client
        self.user_fixture = user_fixture

    def _login(self):
        login_user(self.user_fixture.user, remember=True)
        login_user_via_session(self.client, email=self.user_fixture.email)

    def post(self, *args, **kwargs):
        self._login()
        return self.client.post(*args, **kwargs)

    def get(self, *args, **kwargs):
        self._login()
        return self.client.get(*args, **kwargs)

    def put(self, *args, **kwargs):
        self._login()
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._login()
        return self.client.delete(*args, **kwargs)


@pytest.fixture()
def logged_client(client):
    def _logged_client(user):
        return LoggedClient(client, user)

    return _logged_client


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
def example_topic_draft(record_service, users, default_workflow_json):  # needed for ui
    identity = users[0].identity
    draft = record_service.create(identity, default_workflow_json)
    return draft._obj


@pytest.fixture()
def record_factory(record_service, default_workflow_json):
    def record(identity, custom_workflow=None, additional_data=None):
        json = copy.deepcopy(default_workflow_json)
        if custom_workflow:  # specifying this assumes use of workflows
            json["parent"]["workflow"] = custom_workflow
        json = {
            "metadata": {
                "title": "Title",
                "creators": [
                    "Creator 1",
                    "Creator 2",
                ],
                "contributors": ["Contributor 1"],
            },
            **json,
        }
        if additional_data:
            json |= additional_data
        draft = record_service.create(identity, json)
        record = record_service.publish(system_identity, draft.id)
        return record._obj

    return record


@pytest.fixture()
def create_draft_via_resource(default_workflow_json, urls):
    def _create_draft(
        client, expand=True, custom_workflow=None, additional_data=None, **kwargs
    ):
        json = copy.deepcopy(default_workflow_json)
        if custom_workflow:
            json["parent"]["workflow_id"] = custom_workflow
        if additional_data:
            json |= additional_data
        url = urls["BASE_URL"] + "?expand=true" if expand else urls["BASE_URL"]
        return client.post(url, json=json, **kwargs)

    return _create_draft


@pytest.fixture()
def events_resource_data():
    """Input data for the Request Events Resource (REST body)."""
    return {
        "payload": {
            "content": "This is a comment.",
            "format": RequestEventFormat.HTML.value,
        }
    }


def _create_role(id, name, description, is_managed, database):
    """Creates a Role/Group."""
    r = current_datastore.create_role(
        id=id, name=name, description=description, is_managed=is_managed
    )
    current_datastore.commit()
    return r


@pytest.fixture()
def role(database):
    """A single group."""
    r = _create_role(
        id="it-dep",
        name="it-dep",
        description="IT Department",
        is_managed=False,
        database=database,
    )
    return r


@pytest.fixture()
def role_ui_serialization():
    return {
        "label": "it-dep",
        "links": {"self": "https://127.0.0.1:5000/api/groups/it-dep"},
        "reference": {"group": "it-dep"},
        "type": "group",
    }


@pytest.fixture()
def default_workflow_json():
    return {"parent": {"workflow_id": "default"}}
