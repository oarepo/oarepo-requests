#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Small reproducers for LIBRARY_REVIEW.md; assertions describe correct behavior.

These are intentionally failing regression tests for unfixed findings, not xfails.
The numbers match the report, with its three smaller issues numbered 14--16.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_db.uow import UnitOfWork
from invenio_notifications.models import Notification, Recipient
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services import SearchOptions
from invenio_requests.records.api import Request
from invenio_search.engine import dsl
from oarepo_runtime.typing import record_from_result
from oarepo_workflows.proxies import current_oarepo_workflows

from oarepo_requests.errors import OpenRequestAlreadyExistsError, UnresolvedRequestsError, VersionAlreadyExists
from oarepo_requests.notifications.filters import UsersWithNoMailRecipientFilter
from oarepo_requests.notifications.generators.context import NotificationCtxWithReference, ReferenceSavingEntityResolve
from oarepo_requests.notifications.generators.recipients import EntityRecipientGenerator
from oarepo_requests.records.dumpers import RecordReferenceDumperExt
from oarepo_requests.services.facets.params import RequestNotOwnerFilterParam, RequestOwnerFilterParam
from oarepo_requests.types.publish_base import PublishRequestType
from oarepo_requests.types.publish_draft import PublishDraftRequestType
from oarepo_requests.types.publish_new_version import PublishNewVersionRequestType
from oarepo_requests.utils import search_requests


@pytest.fixture(autouse=True)
def review_environment(app, db, search_clear, monkeypatch):
    # Exercise request persistence without dispatching unrelated email/Celery jobs.
    monkeypatch.setattr(NotificationOp, "on_post_commit", lambda _self, _uow: None)


class ReviewAcceptError(RuntimeError):
    """An intentional failure after the action has changed the topic."""


@pytest.fixture
def fail_accept(app, monkeypatch):
    class FailingComponent:
        def accept(self, *_args: object, **_kwargs: object) -> None:
            raise ReviewAcceptError("failure after topic mutation")

    monkeypatch.setitem(
        app.config,
        "REQUESTS_ACTION_COMPONENTS",
        [FailingComponent, *app.config["REQUESTS_ACTION_COMPONENTS"]],
    )


def one_result_per_page(monkeypatch, service, option_name, sort_fields):
    """Use real search pagination, with two documents sufficient to expose truncation."""
    options = getattr(service.config, option_name)
    one_result = type(
        "ReviewSearchOptions",
        (options,),
        {
            "pagination_options": {**options.pagination_options, "default_results_per_page": 1},
            "sort_default_no_query": "review_order",
            "sort_options": {"review_order": {"fields": sort_fields}},
            "available_sort_options": {"review_order": {"fields": sort_fields}},
        },
    )
    monkeypatch.setattr(service.config, option_name, one_result)


def test_review_01_new_version_is_applicable(record_factory, record_service, users):
    """A valid new-version draft must expose its publication request."""
    record = record_factory(users[0].identity)
    draft = record_from_result(record_service.new_version(system_identity, record["id"]))

    assert PublishNewVersionRequestType.is_applicable_to(system_identity, draft)


def test_review_02_failed_accept_rolls_back_deletion(
    db,
    record_factory,
    record_service,
    requests_service,
    submit_request_on_record,
    users,
    fail_accept,
):
    """A later accept failure must leave the published record undeleted."""
    record = record_factory(users[0].identity)
    request = submit_request_on_record(
        system_identity,
        record["id"],
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )

    with pytest.raises(ReviewAcceptError, match="after topic mutation"):
        requests_service.execute_action(system_identity, request.id, "accept")

    db.session.expire_all()
    assert Request.get_record(request.id).status == "submitted"
    assert not record_service.record_cls.pid.resolve(record["id"]).deletion_status.is_deleted


@pytest.mark.parametrize("keep_files", ["no", "yes"])
def test_review_03_failed_accept_rolls_back_new_version(
    db,
    record_with_files_factory,
    record_service,
    requests_service,
    submit_request_on_record,
    users,
    fail_accept,
    keep_files,
):
    """Keeping files must not cause the new draft to survive an accept failure."""
    record = record_with_files_factory(users[0].identity, custom_workflow="different_recipients")
    request = submit_request_on_record(
        system_identity,
        record["id"],
        "new_version",
        create_additional_data={"payload": {"keep_files": keep_files}},
    )

    with pytest.raises(ReviewAcceptError, match="after topic mutation"):
        requests_service.execute_action(system_identity, request.id, "accept")

    db.session.expire_all()
    assert Request.get_record(request.id).status == "submitted"
    assert record_service.record_cls.pid.resolve(record["id"]).versions.next_draft_id is None


@pytest.mark.parametrize("phase", ["create", "accept"])
def test_review_04_publication_checks_requests_beyond_first_page(
    monkeypatch,
    draft_factory,
    record_service,
    requests_service,
    create_request_on_draft,
    submit_request_on_draft,
    users,
    phase,
):
    """One older nonblocking hit must not hide a newer open blocking request."""
    draft = draft_factory(users[0].identity, custom_workflow="cascade_update")
    if phase == "accept":
        publication = submit_request_on_draft(system_identity, draft["id"], "publish_draft")
    closed = create_request_on_draft(system_identity, draft["id"], "another_topic_updating")
    requests_service.execute_action(system_identity, closed.id, "cancel")
    blocker = create_request_on_draft(system_identity, draft["id"], "another_topic_updating")
    one_result_per_page(monkeypatch, requests_service, "search", ["created"])

    topic = record_from_result(record_service.read_draft(system_identity, draft["id"]))
    page = list(search_requests(system_identity, topic).hits)
    assert len(page) == 1
    assert page[0]["id"] != str(blocker.id)
    assert Request.get_record(blocker.id).is_open

    if phase == "create":
        with pytest.raises(UnresolvedRequestsError):
            create_request_on_draft(system_identity, draft["id"], "publish_draft")
    else:
        with pytest.raises(UnresolvedRequestsError):
            requests_service.execute_action(system_identity, publication.id, "accept")


def test_review_05_duplicate_in_same_unit_of_work_is_rejected(
    draft_factory,
    create_request_on_draft,
    users,
):
    """A second creation must see the first request before indexing/commit."""
    draft = draft_factory(users[0].identity)
    uow = UnitOfWork()
    try:
        create_request_on_draft(system_identity, draft["id"], "publish_draft", uow=uow)
        with pytest.raises(OpenRequestAlreadyExistsError):
            create_request_on_draft(system_identity, draft["id"], "publish_draft", uow=uow)
    finally:
        uow.rollback()


def test_review_06_editing_older_version_is_metadata_publication(record_factory, record_service, users):
    """An edit of v1 remains a metadata edit after v2 has been published."""
    first = record_factory(users[0].identity)
    second = record_service.new_version(system_identity, first["id"])
    record_service.publish(system_identity, second.id)
    edit = record_from_result(record_service.edit(system_identity, first["id"]))
    assert edit.is_published
    assert not edit.versions.is_latest

    assert PublishRequestType.get_topic_type(edit) == "metadata"


def test_review_07_version_is_persisted_without_submitted_transition(
    db,
    monkeypatch,
    draft_factory,
    record_service,
    requests_service,
    users,
):
    """Saving the version payload must not depend on changing workflow state."""
    draft = draft_factory(users[0].identity)
    topic = record_from_result(record_service.read_draft(system_identity, draft["id"]))
    transitions = current_oarepo_workflows.get_workflow(topic).requests()["publish_draft"].transitions
    monkeypatch.setattr(transitions, "submitted", None)
    request = requests_service.create(
        system_identity,
        data={"payload": {"version": "review-v1"}},
        request_type="publish_draft",
        topic=topic,
    )

    requests_service.execute_action(system_identity, request.id, "submit")
    db.session.expire_all()
    saved = record_from_result(record_service.read_draft(system_identity, draft["id"]))

    assert saved.metadata.get("version") == "review-v1"


def test_review_08_explicit_creator_can_select_conditional_recipient(
    draft_factory,
    create_request_on_draft,
    users,
):
    """A creator reference must work just as the implicit caller identity does."""
    draft = draft_factory(users[0].identity, custom_workflow="with_ct")
    request = create_request_on_draft(
        system_identity,
        draft["id"],
        "conditional_recipient_rt",
        creator={"user": str(users[0].id)},
    )

    assert request.to_dict()["receiver"] == {"user": str(users[1].id)}


def test_review_09_explicit_expiration_is_stored(draft_factory, create_request_on_draft, users):
    """The service must pass the supplied expiration deadline to persistence."""
    draft = draft_factory(users[0].identity)
    deadline = datetime.now(UTC) + timedelta(days=1)
    request = create_request_on_draft(
        system_identity,
        draft["id"],
        "publish_draft",
        expires_at=deadline,
    )

    assert Request.get_record(request.id).expires_at == deadline


def test_review_10_receiver_uses_converted_draft(
    app,
    monkeypatch,
    record_factory,
    record_service,
    requests_service,
    users,
):
    """Metadata-publication routing must inspect the draft, not the published record."""
    record = record_factory(users[0].identity)
    record_service.edit(system_identity, record["id"])
    published = record_from_result(record_service.read(system_identity, record["id"]))

    def receiver_for_topic(*, record, **_kwargs: object) -> dict[str, str]:
        return {"user": str(users[1 if record.is_draft else 2].id)}

    monkeypatch.setattr(app.extensions["oarepo-requests"], "default_request_receiver_function", receiver_for_topic)
    request = requests_service.create(
        system_identity,
        data={},
        request_type="publish_changed_metadata",
        topic=published,
    )

    assert request.to_dict()["receiver"] == {"user": str(users[1].id)}


def test_review_11_missing_receiver_contributes_no_notification_recipients():
    """An optional null receiver must not abort notification recipient generation."""
    context = NotificationCtxWithReference(
        {"request": "example"},
        "request",
        {"request": {"receiver": None}},
    )
    notification = Notification(type="review", context=context)
    ReferenceSavingEntityResolve("request.receiver")(notification)
    creator = Recipient(data={"id": "1", "email": "creator@example.org"})
    recipients = {"1": creator}

    EntityRecipientGenerator("request.receiver")(notification, recipients)

    assert recipients == {"1": creator}


@pytest.mark.parametrize("topic", [{"record": "example"}, [{"record": "example"}, {"articles": "example"}]])
def test_review_12_topic_dumper_loads_old_and_new_index_documents(topic):
    """A mixed index must support the original dictionary and the newer array."""
    data = {"topic": deepcopy(topic)}

    RecordReferenceDumperExt().load(data, Request)

    assert data["topic"] == {"record": "example"}


@pytest.mark.parametrize("phase", ["create", "submit"])
def test_review_13_duplicate_version_label_beyond_first_page_is_rejected(
    monkeypatch,
    record_factory,
    record_service,
    requests_service,
    create_request_on_draft,
    users,
    phase,
):
    """The older of two versions must still reserve its version label."""
    first = record_factory(users[0].identity, additional_data={"metadata": {"version": "review-v1"}})
    second = record_service.new_version(system_identity, first["id"])
    record_service.update_draft(
        system_identity,
        second.id,
        {"metadata": {**first["metadata"], "version": "review-v2"}, "files": first["files"]},
    )
    record_service.publish(system_identity, second.id)
    record_service.record_cls.index.refresh()
    third = record_service.new_version(system_identity, second.id)
    one_result_per_page(monkeypatch, record_service, "search_versions", ["-versions.index"])
    page = list(record_service.search_versions(system_identity, third.id).hits)
    assert len(page) == 1
    assert page[0]["metadata"]["version"] == "review-v2"

    if phase == "submit":
        request = create_request_on_draft(system_identity, third.id, "publish_new_version")
        requests_service.update(system_identity, request.id, {"payload": {"version": "review-v1"}})

    if phase == "create":
        with pytest.raises(VersionAlreadyExists):
            create_request_on_draft(
                system_identity,
                third.id,
                "publish_new_version",
                additional_data={"payload": {"version": "review-v1"}},
            )
    else:
        with pytest.raises(VersionAlreadyExists):
            requests_service.execute_action(system_identity, request.id, "submit")


@pytest.mark.parametrize(
    ("filter_cls", "param"), [(RequestOwnerFilterParam, "mine"), (RequestNotOwnerFilterParam, "assigned")]
)
def test_review_14_false_owner_filter_is_inactive(filter_cls, param):
    """Sending false should have the same effect as omitting the filter."""
    interpreter = filter_cls(param, "created_by.user", SearchOptions)
    search = dsl.Search()

    omitted = interpreter.apply(Identity(1), search, {})
    disabled = interpreter.apply(Identity(1), search, {param: False})

    assert disabled.to_dict() == omitted.to_dict()


def test_review_15_no_email_filter_works_through_builder():
    """The builder consumes in-place changes, not the filter's return value."""

    class Builder(NotificationBuilder):
        recipient_filters = (UsersWithNoMailRecipientFilter(),)

    recipients = {
        "valid": Recipient(data={"email": "user@example.org"}),
        "missing": Recipient(data={"id": "2"}),
    }

    filtered = Builder.filter_recipients(Notification(type="review", context={}), recipients)

    assert set(filtered) == {"valid"}


def test_review_16_invalid_topic_error_names_actual_type(record_factory, record_service, users):
    """An initial-publication request on a new-version draft should name its type."""
    record = record_factory(users[0].identity)
    draft = record_from_result(record_service.new_version(system_identity, record["id"]))

    with pytest.raises(ValueError, match="Topic type new_version"):
        PublishDraftRequestType().can_create(system_identity, {}, {}, draft, {})


def test_review_17_new_version_of_older_version_follows_latest(
    record_factory,
    record_service,
    submit_request_on_record,
    users,
):
    """A new version requested on v1 after v2 was published becomes v3 of the same record."""
    first = record_factory(users[0].identity)
    second = record_service.new_version(system_identity, first["id"])
    record_service.publish(system_identity, second.id)
    assert not record_service.record_cls.pid.resolve(first["id"]).versions.is_latest

    request = submit_request_on_record(users[0].identity, first["id"], "new_version")

    assert request.to_dict()["status"] == "accepted"
    created_id = request.to_dict()["payload"]["created_topic"].split(":")[1]
    created = record_from_result(record_service.read_draft(system_identity, created_id))
    assert created.parent.id == record_service.record_cls.pid.resolve(first["id"]).parent.id
    assert created.versions.index == 3
    assert created.versions.next_draft_id == created.id
