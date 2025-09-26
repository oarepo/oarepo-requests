#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

import base64
import json
import os
import time
from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar

import pytest
from invenio_i18n import _
from invenio_rdm_records.services.generators import RecordOwners
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
from invenio_users_resources.records import UserAggregate
from oarepo_model.customizations import AddFileToModule
from oarepo_model.presets.ui import ui_preset
from oarepo_model.presets.ui_links import ui_links_preset
from oarepo_rdm import rdm_preset
from oarepo_workflows import (
    AutoApprove,
    AutoRequest,
    IfInState,
    WorkflowRequest,
    WorkflowRequestEscalation,
    WorkflowRequestPolicy,
    WorkflowTransitions,
)
from oarepo_workflows.base import Workflow
from oarepo_workflows.model.presets import workflows_preset
from oarepo_workflows.requests.events import WorkflowEvent
from pytest_oarepo.requests.classes import (
    CSLocaleUserGenerator,
    TestEventType,
    UserGenerator,
)
from pytest_oarepo.users import _create_user

from oarepo_requests.actions.generic import (
    OARepoAcceptAction,
    OARepoDeclineAction,
    OARepoSubmitAction,
)
from oarepo_requests.model.presets.requests import requests_preset
from oarepo_requests.receiver import default_workflow_receiver_function
from oarepo_requests.services.permissions.generators.conditional import (
    IfNoEditDraft,
    IfNoNewVersionDraft,
    IfRequestedBy,
)
from oarepo_requests.services.permissions.workflow_policies import (
    RequestBasedWorkflowPermissions,
)
from oarepo_requests.types import (
    ModelRefTypes,
    NonDuplicableOARepoRequestType,
)
from oarepo_requests.types.events.topic_update import TopicUpdateEventType

if TYPE_CHECKING:
    from invenio_requests.customizations.actions import RequestAction

pytest_plugins = [
    "pytest_oarepo.requests.fixtures",
    "pytest_oarepo.records",
    "pytest_oarepo.fixtures",
    "pytest_oarepo.users",
    "pytest_oarepo.files",
]


@pytest.fixture
def events_service():
    from invenio_requests.proxies import current_events_service

    return current_events_service


@pytest.fixture(scope="module", autouse=True)
def location(location):
    return location


"""
@pytest.fixture(autouse=True)
def vocab_cf(vocab_cf):
    return vocab_cf
"""


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

"""
def _override(original: tuple[WorkflowRequest], *new_):
    to_remove = []
    for n in new_:
        for o in original:
            if n.request_type == o.request_type:
                to_remove.append(o)
    o_keep = [o for o in original if o not in to_remove]
    return (*o_keep, *new_)
"""


class GenericTestableRequestType(NonDuplicableOARepoRequestType):
    """Generic usable request type for tests."""

    type_id = "generic"
    name = _("Generic")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Generic request that doesn't do anything")
    receiver_can_be_none = False
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)


class ApproveRequestType(NonDuplicableOARepoRequestType):
    """Request type for approving before publish."""

    type_id = "approve_draft"
    name = _("Approve draft")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request approving of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class AnotherTopicUpdatingRequestType(NonDuplicableOARepoRequestType):
    """Generic request type with topic change on topic update."""

    type_id = "another_topic_updating"
    name = _("Another topic updating")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request to test cascade update of live topic")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    def topic_change(self, request: Request, new_topic: dict, uow):
        """Update topic on topic update."""
        request.topic = new_topic
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))


class ConditionalRecipientRequestType(NonDuplicableOARepoRequestType):
    """Generic request type with conditional recipient."""

    type_id = "conditional_recipient_rt"
    name = _("Request type to test conditional recipients")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("A no-op request to check conditional recipients")
    receiver_can_be_none = False
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class DefaultRequests(WorkflowRequestPolicy):
    """Default test requests workflow."""

    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2)],
        transitions=WorkflowTransitions(
            submitted="publishing",
            accepted="published",
            declined="draft",
            cancelled="draft",
        ),
        escalations=[
            WorkflowRequestEscalation(
                after=timedelta(seconds=2),
                recipients=[
                    UserGenerator(3),
                ],
            ),
            WorkflowRequestEscalation(
                after=timedelta(seconds=6),
                recipients=[
                    UserGenerator(4),
                ],
            ),
            WorkflowRequestEscalation(
                after=timedelta(seconds=10),
                recipients=[
                    UserGenerator(5),
                ],
            ),
        ],
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


class DifferentLocalesPublish(WorkflowRequestPolicy):
    """Different locales test requests workflow."""

    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[CSLocaleUserGenerator()],
        transitions=WorkflowTransitions(
            submitted="publishing",
            accepted="published",
            declined="draft",
            cancelled="draft",
        ),
    )
    delete_published_record = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[UserGenerator(1), CSLocaleUserGenerator()],
        transitions=WorkflowTransitions(
            submitted="deleting",
            accepted="deleted",
            declined="published",
            cancelled="published",
        ),
        events=events_only_receiver_can_comment,
    )


class RequestWithMultipleRecipients(WorkflowRequestPolicy):
    """Multiple recipients test requests workflow."""

    publish_draft = WorkflowRequest(
        requesters=[IfInState("draft", [RecordOwners()])],
        recipients=[UserGenerator(2), UserGenerator(1)],
        transitions=WorkflowTransitions(
            submitted="publishing",
            accepted="published",
            declined="draft",
            cancelled="draft",
        ),
        escalations=[
            WorkflowRequestEscalation(
                after=timedelta(seconds=2),
                recipients=[UserGenerator(3), UserGenerator(7)],
            ),
            WorkflowRequestEscalation(
                after=timedelta(seconds=6),
                recipients=[
                    UserGenerator(4),
                ],
            ),
            WorkflowRequestEscalation(
                after=timedelta(seconds=10),
                recipients=[
                    UserGenerator(5),
                ],
            ),
            WorkflowRequestEscalation(
                after=timedelta(seconds=14),
                recipients=[
                    UserGenerator(5),
                    UserGenerator(6),
                ],
            ),
        ],
    )


class RequestsWithDifferentRecipients(DefaultRequests):
    """Alternative recipients to default test requests workflow."""

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


class RequestsWithApproveWithoutGeneric(WorkflowRequestPolicy):
    """Publish needs approval before publishing test requests workflow."""

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


class RequestsWithApprove(WorkflowRequestPolicy):
    """Publish needs approval before publishing test requests workflow."""

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
    generic = WorkflowRequest(
        requesters=[IfInState("draft", [AutoRequest()])],
        recipients=[UserGenerator(1)],
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
    """With conditional recipient test requests workflow."""

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
    """Test requests workflow with another topic updating request."""

    another_topic_updating = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[UserGenerator(2)],
    )


class RequestsWithSystemIdentity(WorkflowRequestPolicy):
    """Test requests workflow with publish only by system identity."""

    publish_draft = WorkflowRequest(
        requesters=[AnyUser()],
        recipients=[UserGenerator("system")],
    )


class GenericTestableRequestType(NonDuplicableOARepoRequestType):
    """Generic usable request type for tests."""

    type_id = "generic"
    name = _("Generic")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Generic request that doesn't do anything")
    receiver_can_be_none = False
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)


class ApproveRequestType(NonDuplicableOARepoRequestType):
    """Request type for approving before publish."""

    type_id = "approve_draft"
    name = _("Approve draft")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request approving of a draft")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class AnotherTopicUpdatingRequestType(NonDuplicableOARepoRequestType):
    """Generic request type with topic change on topic update."""

    type_id = "another_topic_updating"
    name = _("Another topic updating")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("Request to test cascade update of live topic")
    receiver_can_be_none = True
    allowed_topic_ref_types = ModelRefTypes(published=True, draft=True)

    def topic_change(self, request: Request, new_topic: dict, uow):
        """Update topic on topic update."""
        request.topic = new_topic
        uow.register(RecordCommitOp(request, indexer=current_requests_service.indexer))


class ConditionalRecipientRequestType(NonDuplicableOARepoRequestType):
    """Generic request type with conditional recipient."""

    type_id = "conditional_recipient_rt"
    name = _("Request type to test conditional recipients")

    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
        **NonDuplicableOARepoRequestType.available_actions,
        "accept": OARepoAcceptAction,
        "submit": OARepoSubmitAction,
        "decline": OARepoDeclineAction,
    }
    description = _("A no-op request to check conditional recipients")
    receiver_can_be_none = False
    allowed_topic_ref_types = ModelRefTypes(published=False, draft=True)


class TestWorkflowPermissions(RequestBasedWorkflowPermissions):
    """Default workflow permissions for testing."""

    can_read = (
        IfInState("draft", [RecordOwners()]),
        IfInState("publishing", [RecordOwners(), UserGenerator(2)]),
        IfInState("published", [AnyUser()]),
        IfInState("published", [AuthenticatedUser()]),
        IfInState("deleting", [AnyUser()]),
    )
    can_manage_files = (RecordOwners(),)


class WithApprovalPermissions(TestWorkflowPermissions):
    """Default workflow permissions for testing requests with publish approval."""

    can_read = (
        IfInState("draft", [RecordOwners()]),
        IfInState("approving", [RecordOwners(), UserGenerator(2)]),
        IfInState("approved", [RecordOwners(), UserGenerator(2)]),
        IfInState("publishing", [RecordOwners(), UserGenerator(2)]),
        IfInState("published", [AuthenticatedUser()]),
        IfInState("deleting", [AuthenticatedUser()]),
    )


class DifferentLocalesPermissions(TestWorkflowPermissions):
    """Default workflow permissions for testing with multiple locales."""

    can_read = (
        IfInState("draft", [RecordOwners()]),
        IfInState("publishing", [RecordOwners(), CSLocaleUserGenerator()]),
        IfInState("published", [AnyUser()]),
        IfInState("published", [AuthenticatedUser()]),
        IfInState("deleting", [AnyUser()]),
    )


WORKFLOWS = [
    Workflow(
        code="default",
        label=_("Default workflow"),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=DefaultRequests,
    ),
    Workflow(
        code="with_approve",
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithApprove,
    ),
    Workflow(
        code="with_approve_without_generic",
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithApproveWithoutGeneric,
    ),
    Workflow(
        code="with_ct",
        label=_("Workflow with approval process"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithCT,
    ),
    Workflow(
        code="cascade_update",
        label=_("Workflow to test update of live topic"),
        permission_policy_cls=WithApprovalPermissions,
        request_policy_cls=RequestsWithAnotherTopicUpdatingRequestType,
    ),
    Workflow(
        code="different_recipients",
        label=_(
            "Workflow with draft requests with different recipients to test param interpreters"
        ),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=RequestsWithDifferentRecipients,
    ),
    Workflow(
        code="multiple_recipients",
        label=_("Workflow with multiple recipient to test escalation of the request"),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=RequestWithMultipleRecipients,
    ),
    Workflow(
        code="system_identity",
        label=_("Workflow with system identity"),
        permission_policy_cls=TestWorkflowPermissions,
        request_policy_cls=RequestsWithSystemIdentity,
    ),
    Workflow(
        code="different_locales",
        label=_("User with id 3 prefers cs locale."),
        permission_policy_cls=DifferentLocalesPermissions,
        request_policy_cls=DifferentLocalesPublish,
    ),
]


@pytest.fixture
def urls():
    return {"BASE_URL": "/requests-test", "BASE_URL_REQUESTS": "/requests/"}


@pytest.fixture
def serialization_result():
    def _result(topic_id: str, request_id: str) -> dict[str, str | bool | int]:
        return {
            "id": request_id,
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
            "topic": {"requests_test_draft": topic_id},
        }

    return _result


@pytest.fixture
def ui_serialization_result():
    # TODO: correct time formats, translations etc
    def _result(topic_id, request_id) -> dict[str, str | bool | int]:
        return {
            "created_by": {
                "label": "id: 1",
                "links": {"self": "https://127.0.0.1:5000/api/users/1"},
                "reference": {"user": "1"},
                "type": "user",
            },
            "description": "Request to publish a draft",
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
                "label": "blabla",
                "links": {
                    "self": f"https://127.0.0.1:5000/api/requests_test/{topic_id}/draft",
                    "self_html": f"https://127.0.0.1:5000/requests_test/{topic_id}/preview",
                },
                "reference": {"requests_test_draft": topic_id},
                "type": "requests_test_draft",
            },
            "type": "publish_draft",
        }

    return _result


@pytest.fixture(scope="module")
def app_config(app_config, requests_model):
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
        GenericTestableRequestType(),
    ]
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"
    app_config["MAIL_DEFAULT_SENDER"] = "test@invenio-rdm-records.org"

    app_config["I18N_LANGUAGES"] = [("cs", "Czech")]
    app_config["BABEL_DEFAULT_LOCALE"] = "en"

    app_config["APP_THEME"] = ["oarepo", "semantic-ui"]

    app_config["REST_CSRF_ENABLED"] = False
    app_config["RDM_PERSISTENT_IDENTIFIERS"] = {}
    app_config["RDM_OPTIONAL_DOI_VALIDATOR"] = (
        lambda _draft, _previous_published, **_kwargs: True
    )
    app_config["RDM_RECORDS_ALLOW_RESTRICTION_AFTER_GRACE_PERIOD"] = True

    app_config["CELERY_ALWAYS_EAGER"] = True
    app_config["CELERY_TASK_ALWAYS_EAGER"] = True

    return app_config


@pytest.fixture
def check_publish_topic_update():
    def _check_publish_topic_update(
        creator_client, urls, record, before_update_response
    ) -> None:
        request_id = before_update_response["id"]
        record_id = record["id"]

        after_update_response = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}{request_id}"
        ).json
        RequestEvent.index.refresh()
        events = creator_client.get(
            f"{urls['BASE_URL_REQUESTS']}extended/{request_id}/timeline"
        ).json["hits"]["hits"]

        assert before_update_response["topic"] == {"requests_test_draft": record_id}
        assert after_update_response["topic"] == {"requests_test": record_id}

        topic_updated_events = [
            e for e in events if e["type"] == TopicUpdateEventType.type_id
        ]
        assert len(topic_updated_events) == 1
        assert (
            topic_updated_events[0]["payload"]["old_topic"]
            == f"requests_test_draft.{record_id}"
        )
        assert (
            topic_updated_events[0]["payload"]["new_topic"]
            == f"requests_test.{record_id}"
        )

    return _check_publish_topic_update


@pytest.fixture
def user_links():
    def _user_links(user_id) -> dict[str, str]:
        return {
            "avatar": f"https://127.0.0.1:5000/api/users/{user_id}/avatar.svg",
            "records_html": f"https://127.0.0.1:5000/search/records?q=parent.access.owned_by.user:{user_id}",
            "self": f"https://127.0.0.1:5000/api/users/{user_id}",
        }

    return _user_links


# TODO: use pytest-oarepo instead of this
@pytest.fixture
def password():
    """Password fixture."""
    return base64.b64encode(os.urandom(16)).decode("utf-8")


@pytest.fixture
def more_users(app, db, UserFixture, password):  # noqa N803
    if db.engine.dialect.name == "postgresql":
        from sqlalchemy import text
        from invenio_accounts.models import User

        name = User.__table__.name
        sql = f'ALTER SEQUENCE "{name}_id_seq" RESTART WITH 1'
        db.session.execute(text(sql))
        db.session.commit()

    user1 = UserFixture(
        email="user1@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user1, app, db)

    user2 = UserFixture(
        email="user2@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user2, app, db)

    user3 = UserFixture(
        email="user3@example.org",
        password=password,
        user_profile={
            "full_name": "Maxipes Fik",
            "affiliations": "CERN",
        },
        active=True,
        confirmed=True,
    )
    _create_user(user3, app, db)

    user4 = UserFixture(
        email="user4@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user4, app, db)

    user5 = UserFixture(
        email="user5@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user5, app, db)

    user6 = UserFixture(
        email="user6@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user6, app, db)

    user7 = UserFixture(
        email="user7@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user7, app, db)

    user10 = UserFixture(
        email="user10@example.org",
        password=password,
        active=True,
        confirmed=True,
    )
    _create_user(user10, app, db)

    db.session.commit()
    UserAggregate.index.refresh()
    return [user1, user2, user3, user4, user5, user6, user7, user10]


@pytest.fixture(scope="session")
def model_types():
    """Model types fixture."""
    # Define the model types used in the tests
    return {
        "Metadata": {
            "properties": {
                "title": {"type": "fulltext+keyword", "required": True},
            }
        }
    }


@pytest.fixture(scope="session")
def requests_model(model_types):
    from oarepo_model.api import model
    from oarepo_model.presets.drafts import drafts_preset
    from oarepo_model.presets.records_resources import records_resources_preset

    time.time()

    workflow_model = model(
        name="requests_test",
        version="1.0.0",
        presets=[
            records_resources_preset,
            drafts_preset,
            ui_preset,
            ui_links_preset,
            rdm_preset,
            workflows_preset,
            requests_preset,
        ],
        types=[model_types],
        metadata_type="Metadata",
        customizations=[
            AddFileToModule(
                "parent-jsonschema",
                "jsonschemas",
                "parent-v1.0.0.json",
                json.dumps(
                    {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "$id": "local://parent-v1.0.0.json",
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                    }
                ),
            ),
        ],
    )
    workflow_model.register()

    time.time()

    try:
        yield workflow_model
    finally:
        workflow_model.unregister()

    return workflow_model


@pytest.fixture
def record_service(requests_model):
    return requests_model.proxies.current_service
