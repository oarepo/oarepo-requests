#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
import os
from typing import Dict

import pytest
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    SystemProcess,
)
from invenio_records_resources.services.uow import RecordCommitOp
from invenio_requests.customizations import CommentEventType, LogEventType
from invenio_requests.proxies import current_requests_service
from invenio_requests.records.api import Request, RequestEvent
from invenio_requests.services.generators import Receiver
from invenio_requests.services.permissions import (
    PermissionPolicy as InvenioRequestsPermissionPolicy,
)
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
from pytest_oarepo.requests.classes import TestEventType, UserGenerator
from thesis.proxies import current_service

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

pytest_plugins = [
    "pytest_oarepo.requests.fixtures",
    "pytest_oarepo.records",
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
    "pytest_oarepo.files"
]

@pytest.fixture()
def record_service():
    return current_service

@pytest.fixture(scope="module", autouse=True)
def location(location):
    return location


@pytest.fixture(autouse=True)
def vocab_cf(vocab_cf):
    return vocab_cf


can_comment_only_receiver = [
    Receiver(),
    SystemProcess(),
]

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


class DefaultRequests(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="publishing",
            accepted="published",
            declined="draft",
            cancelled="draft",
        ),
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="deleting",
            accepted="deleted",
            declined="published",
            cancelled="published",
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
    edit_published_record = WorkflowRequest(
        requesters=[IfNoEditDraft([IfInState("published", [RecordOwners()])])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(),
    )
    new_version = WorkflowRequest(
        requesters=[IfNoNewVersionDraft([IfInState("published", [RecordOwners()])])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(),
    )


class RequestsWithApprove(WorkflowRequestPolicy):
    publish_draft = WorkflowRequest(
        requesters=[IfInState("approved", [AutoRequest()])],
        recipients=[UserGenerator(1)],
        transitions=WorkflowTransitions(
            submitted="publishing",
            accepted="published",
            declined="approved",
            cancelled="approved",
        ),
        events=events_only_receiver_can_comment,
    )
    approve_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="approving",
            accepted="approved",
            declined="draft",
            cancelled="draft",
        ),
        events=events_only_receiver_can_comment,
    )
    delete_published_record = WorkflowRequest(
        requesters=[IfInState("published", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="deleting",
            accepted="deleted",
            declined="published",
            cancelled="published",
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
    approve_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[],
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

"""
@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    return create_api
"""


@pytest.fixture()
def urls():
    return {"BASE_URL": "/thesis/", "BASE_URL_REQUESTS": "/requests/"}


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


@pytest.fixture(scope="module")
def record_service():
    return current_service


@pytest.fixture
def check_publish_topic_update():
    def _check_publish_topic_update(
        creator_client, urls, record, before_update_response
    ):
        request_id = before_update_response["id"]
        record_id = record["id"]

        after_update_response = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{request_id}"
        ).json
        RequestEvent.index.refresh()
        events = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}extended/{request_id}/timeline"
        ).json["hits"]["hits"]

        assert before_update_response["topic"] == {"thesis_draft": record_id}
        assert after_update_response["topic"] == {"thesis": record_id}

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
