#
# Copyright (C) 2024 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
from __future__ import annotations

from typing import Any

import pytest
from invenio_i18n import lazy_gettext as _
from invenio_notifications.backends import EmailNotificationBackend
from invenio_notifications.manager import NotificationManager
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import EntityResolve
from invenio_records.dictutils import dict_lookup, dict_set
from invenio_requests.customizations.event_types import CommentEventType
from invenio_requests.proxies import current_events_service
from invenio_users_resources.notifications.generators import UserRecipient
from oarepo_workflows.resolvers.multiple_entities import (
    MultipleEntitiesEntity,
    MultipleEntitiesProxy,
    MultipleEntitiesResolver,
)

from oarepo_requests.notifications.builders.publish import (
    PublishDraftRequestSubmitNotificationBuilder,
)


def test_publish_notifications(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    assert mail

    creator = users[0]
    receiver = users[1]
    receiver_client = logged_client(receiver)
    draft1 = draft_factory(creator.identity)

    with mail.record_messages() as outbox:
        submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Request to publish record blabla" in sent_mail.subject
        assert 'You have been asked to publish record "blabla".' in sent_mail.body
        assert 'You have been asked to publish record "blabla".' in sent_mail.html

    record = receiver_client.get(f"{urls['BASE_URL']}/{draft1['id']}/draft?expand=true")

    with mail.record_messages() as outbox:
        # Validate that email was sent
        receiver_client.post(
            link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Record 'blabla' has been published" in sent_mail.subject
        assert 'Your record "blabla" has been published. You can see the record at' in sent_mail.body
        assert 'Your record "blabla" has been published. You can see the record at' in sent_mail.html

    draft1 = draft_factory(creator.identity)
    submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
    record = receiver_client.get(f"{urls['BASE_URL']}/{draft1['id']}/draft?expand=true")
    with mail.record_messages() as outbox:
        # Validate that email was sent
        request_html_link = record.json["expanded"]["requests"][0]["links"]["self_html"]
        receiver_client.post(
            link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Request for publishing of record 'blabla' was declined" in sent_mail.subject
        assert request_html_link in sent_mail.html
        assert request_html_link in sent_mail.body


def test_delete_published_notifications(
    app,
    users,
    logged_client,
    record_factory,
    submit_request_on_record,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    assert mail

    creator = users[0]
    receiver = users[1]
    receiver_client = logged_client(receiver)
    record1 = record_factory(creator.identity)

    with mail.record_messages() as outbox:
        submit_request_on_record(
            creator.identity,
            record1["id"],
            "delete_published_record",
            create_additional_data={"payload": {"removal_reason": "test reason"}},
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Request to delete published record blabla" in sent_mail.subject

    with mail.record_messages() as outbox:
        record = receiver_client.get(f"{urls['BASE_URL']}/{record1['id']}?expand=true")
        assert len(outbox) == 0

    with mail.record_messages() as outbox:
        # Validate that email was sent
        request_html_link = record.json["expanded"]["requests"][0]["links"]["self_html"]
        receiver_client.post(
            link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Published record has been deleted" in sent_mail.subject
        assert request_html_link in sent_mail.html
        assert request_html_link in sent_mail.body

    record1 = record_factory(creator.identity)
    submit_request_on_record(
        creator.identity,
        record1["id"],
        "delete_published_record",
        create_additional_data={"payload": {"removal_reason": "test reason"}},
    )
    record = receiver_client.get(f"{urls['BASE_URL']}/{record1['id']}?expand=true")

    with mail.record_messages() as outbox:
        # Validate that email was sent
        request_html_link = record.json["expanded"]["requests"][0]["links"]["self_html"]
        receiver_client.post(
            link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["decline"]),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]

        assert "Request for deletion of record 'blabla' was declined" in sent_mail.subject
        assert request_html_link in sent_mail.html
        assert request_html_link in sent_mail.body


@pytest.mark.skip("Not yet implemented")
def test_group(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    add_user_in_role,
    role,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    config_restore = app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]
    add_user_in_role(users[0], role)
    add_user_in_role(users[1], role)

    def current_receiver(record=None, request_type=None, **kwargs: Any) -> Any:
        if request_type.type_id == "publish_draft":
            return role
        return config_restore(record, request_type, **kwargs)

    try:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = current_receiver

        creator = users[0]
        draft1 = draft_factory(creator.identity)

        with mail.record_messages() as outbox:
            submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
            assert len(outbox) == 2
            receivers = {m.recipients[0] for m in outbox}
            assert receivers == {"user1@example.org", "user2@example.org"}

    finally:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = config_restore


@pytest.mark.skip("Not yet implemented")
def test_group_multiple_recipients(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    add_user_in_role,
    role,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    config_restore = app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"]
    add_user_in_role(users[0], role)
    add_user_in_role(users[1], role)

    def current_receiver(record=None, request_type=None, **kwargs: Any) -> Any:
        if request_type.type_id == "publish_draft":
            return MultipleEntitiesProxy(
                MultipleEntitiesResolver(),
                {"multiple": MultipleEntitiesEntity.create_id([{"user": users[2].id}, {"group": "it-dep"}])},
            ).resolve()
        return config_restore(record, request_type, **kwargs)

    try:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = current_receiver

        creator = users[0]
        draft1 = draft_factory(creator.identity)

        with mail.record_messages() as outbox:
            submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")
            assert len(outbox) == 3
            receivers = {m.recipients[0] for m in outbox}
            assert receivers == {
                "user1@example.org",
                "user2@example.org",
                "user3@example.org",
            }

    finally:
        app.config["OAREPO_REQUESTS_DEFAULT_RECEIVER"] = config_restore


def test_locale(
    app,
    users,
    user_with_cs_locale,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    assert mail

    en_creator = users[1]
    cs_receiver = user_with_cs_locale
    receiver_client = logged_client(cs_receiver)
    draft1 = draft_factory(en_creator.identity, custom_workflow="different_locales")

    with mail.record_messages() as outbox:
        submit_request_on_draft(en_creator.identity, draft1["id"], "publish_draft")
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Žádost o publikování záznamu blabla" in sent_mail.subject
        assert 'Byli jste požádáni o publikování záznamu "blabla".' in sent_mail.body
        assert 'Byli jste požádáni o publikování záznamu "blabla".' in sent_mail.body

    record = receiver_client.get(f"{urls['BASE_URL']}/{draft1['id']}/draft?expand=true")

    with mail.record_messages() as outbox:
        # Validate that email was sent
        receiver_client.post(
            link2testclient(record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]),
        )
        # check notification is build on submit
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert "Record 'blabla' has been published" in sent_mail.subject
        assert 'Your record "blabla" has been published. You can see the record at' in sent_mail.body
        assert 'Your record "blabla" has been published. You can see the record at' in sent_mail.html


def test_locale_multiple_recipients(
    app,
    users,
    user_with_cs_locale,
    logged_client,
    record_factory,
    submit_request_on_record,
    link2testclient,
    urls,
):
    """Test notification being built on review submit."""
    mail = app.extensions.get("mail")
    assert mail

    en_creator = users[1]
    cs_receiver = user_with_cs_locale
    record1 = record_factory(en_creator.identity, custom_workflow="different_locales")

    with mail.record_messages() as outbox:
        submit_request_on_record(
            en_creator.identity,
            record1["id"],
            "delete_published_record",
            create_additional_data={"payload": {"removal_reason": "test reason"}},
        )
        # check notification is build on submit
        assert len(outbox) == 2
        sent_mail_cz = [mail for mail in outbox if mail.recipients[0] == cs_receiver.user.email]
        sent_mail_en = [mail for mail in outbox if mail.recipients[0] == users[0].user.email]
        assert len(sent_mail_cz) == len(sent_mail_en) == 1
        assert sent_mail_cz[0].subject == "❗️ Žádost o smazání vypublikovaného záznamu blabla"
        assert sent_mail_en[0].subject == "❗️ Request to delete published record blabla"


def test_comment_notifications(
    app,
    users,
    logged_client,
    draft_factory,
    submit_request_on_draft,
    add_user_in_role,
    role,
    link2testclient,
    urls,
):
    """Test notification being built on publish draft submit."""
    mail = app.extensions.get("mail")
    creator = users[0]
    draft1 = draft_factory(creator.identity)  # so i don't have to create a new workflow
    submit = submit_request_on_draft(creator.identity, draft1["id"], "publish_draft")

    with mail.record_messages() as outbox:
        content = "ceci nes pa une comment"
        current_events_service.create(
            creator.identity,
            submit["id"],
            {"payload": {"content": "ceci nes pa une comment"}},
            CommentEventType,
        )
        assert len(outbox) == 1
        receivers = outbox[0].recipients
        assert set(receivers) == {"user2@example.org"}
        assert content in outbox[0].body


def make_lazy(data):
    if isinstance(data, dict):
        return {key: make_lazy(value) for key, value in data.items()}
    if isinstance(data, list):
        return [make_lazy(item) for item in data]
    if isinstance(data, str):
        return _(data)
    return data


class LazyUserRecipient(UserRecipient):
    """User email recipient generator for a notification."""

    def __call__(self, notification, recipients):
        """Update required recipient information and add backend id."""
        user = dict_lookup(notification.context, self.key)
        recipients[user["id"]] = Recipient(data=make_lazy(user))
        return recipients


class LazyEntityResolve(EntityResolve):
    """Payload generator for a notification using the entity resolvers."""

    def __call__(self, notification):
        """Update required recipient information and add backend id."""
        notification = super().__call__(notification)
        dict_set(
            notification.context,
            self.key,
            make_lazy(dict_lookup(notification.context, self.key)),
        )
        return notification


class LazyPublishDraftRequestSubmitNotificationBuilder(PublishDraftRequestSubmitNotificationBuilder):
    """Publish draft request submit notification builder."""

    context = (
        EntityResolve(key="request"),
        LazyEntityResolve(key="request.topic"),
        LazyEntityResolve(key="request.created_by"),
        LazyEntityResolve(key="request.receiver"),
    )

    recipients = (LazyUserRecipient(key="request.receiver"),)


def test_lazy_string_parsing(app, users, logged_client, draft_factory, create_request_on_draft):
    draft = draft_factory(users[0].identity)
    request = create_request_on_draft(users[0].identity, draft["id"], "publish_draft")

    manager = NotificationManager(
        {EmailNotificationBackend.id: EmailNotificationBackend()},
        {LazyPublishDraftRequestSubmitNotificationBuilder.type: LazyPublishDraftRequestSubmitNotificationBuilder},
    )

    notification = LazyPublishDraftRequestSubmitNotificationBuilder.build(request=request._obj)  # noqa SLF001
    mail = app.extensions.get("mail")
    with mail.record_messages() as outbox:
        manager.handle_broadcast(notification)
        assert len(outbox) == 1
