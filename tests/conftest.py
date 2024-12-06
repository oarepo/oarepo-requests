#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import copy
import os
from io import BytesIO
from typing import Dict

import pytest
from deepmerge import always_merger
from flask_principal import UserNeed
from flask_security import login_user
from invenio_access.permissions import system_identity
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    Generator,
    SystemProcess,
)
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.proxies import current_requests, current_requests_service
from invenio_requests.records.api import Request, RequestEvent, RequestEventFormat
from invenio_requests.services.generators import Receiver
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
from invenio_users_resources.records import UserAggregate
from oarepo_runtime.i18n import lazy_gettext as _
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
from oarepo_workflows.requests.events import WorkflowEvent
from oarepo_workflows.requests.generators import RecipientGeneratorMixin
from thesis.proxies import current_service
from thesis.records.api import ThesisDraft

from oarepo_requests.actions.generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from oarepo_requests.receiver import default_workflow_receiver_function
from oarepo_requests.services.permissions.generators.conditional import (
    IfNoEditDraft,
    IfNoNewVersionDraft,
    IfRequestedBy,
)
from oarepo_requests.services.permissions.workflow_policies import (
    RequestBasedWorkflowPermissions,
)
from oarepo_requests.types import ModelRefTypes, NonDuplicableOARepoRequestType
from oarepo_requests.types.events.topic_update import TopicUpdateEventType
from tests.test_requests.utils import link2testclient

can_comment_only_receiver = [
    Receiver(),
    SystemProcess(),
]


class TestEventType(CommentEventType):
    type_id = "test"
    """"""  # to test permissions


events_only_receiver_can_comment = {
    CommentEventType.type_id: WorkflowEvent(submitters=can_comment_only_receiver),
    LogEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    TopicUpdateEventType.type_id: WorkflowEvent(
        submitters=InvenioRequestsPermissionPolicy.can_create_comment
    ),
    TestEventType.type_id: WorkflowEvent(submitters=can_comment_only_receiver),
}


class UserGenerator(RecipientGeneratorMixin, Generator):
    def __init__(self, user_id):
        self.user_id = user_id

    def needs(self, **kwargs):
        return [UserNeed(self.user_id)]

    def reference_receivers(self, **kwargs):
        return [{"user": str(self.user_id)}]


class DefaultRequests(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="publishing", accepted="published", declined="draft"
        ),
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="deleting", accepted="deleted", declined="published"
        ),
    )
    delete_draft = WorkflowRequest(
        requesters=[
            IfInState("draft", [RecordOwners()]),
            IfInState("publishing", [RecordOwners()]),
        ],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
    )
    edit_published_record = WorkflowRequest(
        requesters=[IfNoEditDraft([IfInState("published", [RecordOwners()])])],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
    )
    new_version = WorkflowRequest(
        requesters=[IfNoNewVersionDraft([IfInState("published", [RecordOwners()])])],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
    )


class RequestsWithDifferentRecipients(DefaultRequests):
    another_topic_updating = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[UserGenerator(1)],
    )


class RequestsWithApprove(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("approved", [AutoRequest()])],
        recipients=[UserGenerator(1)],
        transitions=WorkflowTransitions(
            submitted="publishing", accepted="published", declined="approved"
        ),
        events=events_only_receiver_can_comment,
    )
    approve_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="approving", accepted="approved", declined="draft"
        ),
        events=events_only_receiver_can_comment,
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="deleting", accepted="deleted", declined="published"
        ),
        events=events_only_receiver_can_comment,
    )
    edit_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[AutoApprove()],
        transitions=WorkflowTransitions(),
        events=events_only_receiver_can_comment,
    )


class RequestsWithCT(WorkflowRequestPolicy):
    conditional_recipient_rt = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[
            IfRequestedBy(UserGenerator(1), [UserGenerator(2)], [UserGenerator(3)])
        ],
    )


class RequestsWithAnotherTopicUpdatingRequestType(DefaultRequests):
    another_topic_updating = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[UserGenerator(2)],
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


class AnotherTopicUpdatingRequestType(NonDuplicableOARepoRequestType):
    type_id = "another_topic_updating"
    name = _("Another topic updating")

    available_actions = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request to test cascade update of live topic")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    def topic_change(self, request: Request, new_topic: Dict, uow):
        setattr(request, "topic", new_topic)
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))


class ConditionalRecipientRequestType(NonDuplicableOARepoRequestType):
    type_id = "conditional_recipient_rt"
    name = _("Request type to test conditional recipients")

    available_actions = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("A no-op request to check conditional recipients")
    receiver_can_be_none = False
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class TestWorkflowPermissions(RequestBasedWorkflowPermissions):
    can_read = [
        IfInState("draft", [RecordOwners()]),
        IfInState("publishing", [RecordOwners(), UserGenerator(2)]),
        IfInState("published", [AnyUser()]),
        IfInState("published", [AuthenticatedUser()]),
        IfInState("deleting", [AnyUser()]),
    ]


class WithApprovalPermissions(RequestBasedWorkflowPermissions):
    can_read = [
        IfInState("draft", [RecordOwners()]),
        IfInState("approving", [RecordOwners(), UserGenerator(2)]),
        IfInState("approved", [RecordOwners(), UserGenerator(2)]),
        IfInState("publishing", [RecordOwners(), UserGenerator(2)]),
        IfInState("published", [AuthenticatedUser()]),
        IfInState("deleting", [AuthenticatedUser()]),
    ]


WORKFLOWS = {
    "default": Workflow(
        label=_("Default workflow"),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=DefaultRequests,
    ),
    "with_approve": Workflow(
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithApprove,
    ),
    "with_ct": Workflow(
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithCT,
    ),
    "cascade_update": Workflow(
        label=_("Workflow to test update of live topic"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithAnotherTopicUpdatingRequestType,
    ),
    "different_recipients": Workflow(
        label=_(
            "Workflow with draft requests with different recipients to test param interpreters"
        ),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=RequestsWithDifferentRecipients,
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
            "payload": {"version": "1.0"},
        }

    return ret_data


@pytest.fixture()
def conditional_recipient_request_data_function():
    def ret_data(record_id):
        return {
            "request_type": "conditional_recipient_rt",
            "topic": {"thesis_draft": record_id},
        }

    return ret_data


@pytest.fixture()
def another_topic_updating_request_function():
    def ret_data(record_id):
        return {
            "request_type": "another_topic_updating",
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
def new_version_data_function():
    def ret_data(record_id):
        return {
            "request_type": "new_version",
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
def delete_draft_function():
    def ret_data(record_id):
        return {
            "request_type": "delete_draft",
            "topic": {"thesis_draft": record_id},
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
                "label": "id: 1",
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
                # "label": f"id: {topic_id}",
                "label": "blabla",
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
    app_config["REQUESTS_REGISTERED_EVENT_TYPES"] = [
        TestEventType(),  # remaining are loaded from .config
    ]
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
    app_config["REQUESTS_REGISTERED_TYPES"] = [
        ApproveRequestType(),
        ConditionalRecipientRequestType(),
        AnotherTopicUpdatingRequestType(),
    ]
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"
    return app_config


@pytest.fixture(scope="module", autouse=True)
def location(location):
    return location


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
        username="beetlesmasher",
        active=True,
        confirmed=True,
    )
    user2.create(app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password="beetlesmasher",
        username="beetlesmasherXXL",
        user_profile={
            "full_name": "Maxipes Fik",
            "affiliations": "CERN",
        },
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
                "creators": [
                    "Creator 1",
                    "Creator 2",
                ],
                "contributors": ["Contributor 1"],
            }
        }
        json = always_merger.merge(json, default_workflow_json)
        if additional_data:
            always_merger.merge(json, additional_data)
        draft = record_service.create(identity, json)
        record = record_service.publish(system_identity, draft.id)
        return record._obj

    return record


@pytest.fixture()
def record_with_files_factory(record_service, default_workflow_json):
    def record(identity, custom_workflow=None, additional_data=None):
        json = copy.deepcopy(default_workflow_json)
        if (
            "files" in default_workflow_json
            and "enabled" in default_workflow_json["files"]
        ):
            default_workflow_json["files"]["enabled"] = True
        if custom_workflow:  # specifying this assumes use of workflows
            json["parent"]["workflow"] = custom_workflow
        json = {
            "metadata": {
                "creators": [
                    "Creator 1",
                    "Creator 2",
                ],
                "contributors": ["Contributor 1"],
            }
        }
        json = always_merger.merge(json, default_workflow_json)
        if additional_data:
            always_merger.merge(json, additional_data)
        draft = record_service.create(identity, json)

        # upload file
        # Initialize files upload
        files_service = record_service._draft_files
        init = files_service.init_files(
            identity,
            draft["id"],
            data=[
                {"key": "test.pdf", "metadata": {"title": "Test file"}},
            ],
        )
        upload = files_service.set_file_content(
            identity, draft["id"], "test.pdf", stream=BytesIO(b"testfile")
        )
        commit = files_service.commit_file(identity, draft["id"], "test.pdf")

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
            json["parent"]["workflow"] = custom_workflow
        if additional_data:
            json = always_merger.merge(json, additional_data)
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
        "links": {
            "avatar": "https://127.0.0.1:5000/api/groups/it-dep/avatar.svg",
            "self": "https://127.0.0.1:5000/api/groups/it-dep",
        },
        "reference": {"group": "it-dep"},
        "type": "group",
    }


@pytest.fixture()
def default_workflow_json():
    return {
        "parent": {"workflow": "default"},
        "metadata": {"title": "blabla"},
        "files": {"enabled": False},
    }


@pytest.fixture()
def get_request_type():
    """
    gets request create link from serialized request types
    """

    def _get_request_type(request_types_json, request_type):
        selected_entry = [
            entry for entry in request_types_json if entry["type_id"] == request_type
        ][0]
        return selected_entry

    return _get_request_type


@pytest.fixture()
def get_request_link(get_request_type):
    """
    gets request create link from serialized request types
    """

    def _create_request_from_link(request_types_json, request_type):
        selected_entry = get_request_type(request_types_json, request_type)
        return selected_entry["links"]["actions"]["create"]

    return _create_request_from_link


@pytest.fixture
def create_request_by_link(get_request_link):
    def _create_request(client, record, request_type):
        applicable_requests = client.get(
            link2testclient(record.json["links"]["applicable-requests"])
        ).json["hits"]["hits"]
        create_link = link2testclient(
            get_request_link(applicable_requests, request_type)
        )
        create_response = client.post(create_link)
        return create_response

    return _create_request


@pytest.fixture
def submit_request_by_link(create_request_by_link):
    def _submit_request(client, record, request_type):
        create_response = create_request_by_link(client, record, request_type)
        submit_response = client.post(
            link2testclient(create_response.json["links"]["actions"]["submit"])
        )
        return submit_response

    return _submit_request


@pytest.fixture
def check_publish_topic_update():
    def _check_publish_topic_update(
        creator_client, urls, record, before_update_response
    ):
        request_id = before_update_response.json["id"]
        record_id = record.json["id"]

        after_update_response = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{request_id}"
        )
        RequestEvent.index.refresh()
        events = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}extended/{request_id}/timeline"
        ).json["hits"]["hits"]

        assert before_update_response.json["topic"] == {"thesis_draft": record_id}
        assert after_update_response.json["topic"] == {"thesis": record_id}

        topic_updated_events = [
            e for e in events if e["type"] == TopicUpdateEventType.type_id
        ]
        assert len(topic_updated_events) == 1
        assert (
            topic_updated_events[0]["payload"]["old_topic"]
            == f"thesis_draft.{record_id}"
        )
        assert topic_updated_events[0]["payload"]["new_topic"] == f"thesis.{record_id}"

    return _check_publish_topic_update


@pytest.fixture
def user_links():
    def _user_links(user_id):
        return {
            "avatar": f"https://127.0.0.1:5000/api/users/{user_id}/avatar.svg",
            "records_html": f"https://127.0.0.1:5000/search/records?q=user:{user_id}",
            "self": f"https://127.0.0.1:5000/api/users/{user_id}",
        }

    return _user_links
