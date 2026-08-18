#
# Copyright (C) 2026 CESNET z.s.p.o.
#
# oarepo-requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Tests for notifications sent for group membership requests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from invenio_access import ActionRoles
from invenio_accounts.proxies import current_datastore
from invenio_users_resources.proxies import current_groups_service

if TYPE_CHECKING:
    from invenio_accounts.models import Role


def _create_role(id_: str, name: str, description: str) -> Role:
    """Create a role/group, mirroring pytest_oarepo.roles._create_role."""
    role = current_datastore.create_role(id=id_, name=name, description=description, is_managed=False)
    current_datastore.commit()
    current_groups_service.indexer.process_bulk_queue()
    current_groups_service.indexer.refresh()
    return role


@pytest.fixture
def administration_role(app, db):
    """Create the 'administration' role, the default receiver of group_membership requests.

    Members also get the "administration-moderation" action, as accepting
    a request adds the requester to the target group, which requires it.
    """
    role = _create_role("administration", "administration", "Administrators")

    actions = app.extensions["invenio-access"].actions
    db.session.add(ActionRoles.allow(actions["administration-moderation"], role_id=role.id))
    db.session.commit()
    return role


@pytest.fixture
def submitters_role(db):
    """Create the group that users request membership in."""
    return _create_role("submitters", "submitters", "Submitters")


def test_group_membership_notifications(
    app,
    users,
    requests_service,
    administration_role,
    submitters_role,
    add_user_in_role,
):
    """Submit and accept a group membership request; check notification emails."""
    mail = app.extensions.get("mail")
    assert mail

    requester = users[0]
    administrator = users[1]
    add_user_in_role(administrator, administration_role)

    create_response = requests_service.create(
        requester.identity,
        data={"payload": {"justification": ""}},
        request_type="group_membership",
        topic=submitters_role,
    )
    assert create_response["receiver"] == {"group": "administration"}

    with mail.record_messages() as outbox:
        submit_response = requests_service.execute_action(
            requester.identity, id_=create_response["id"], action="submit"
        )
        # the administrator (member of the "administration" group) is notified
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert sent_mail.recipients == [administrator.email]
        assert "Request for group membership: Submitters" in sent_mail.subject
        assert 'A request has been made to join the group "Submitters".' in sent_mail.body
        assert 'A request has been made to join the group "Submitters".' in sent_mail.html

    with mail.record_messages() as outbox:
        requests_service.execute_action(administrator.identity, id_=submit_response["id"], action="accept")
        # the requester is notified that their request was accepted
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert sent_mail.recipients == [requester.email]
        assert "Your request to join group 'Submitters' has been accepted" in sent_mail.subject
        assert (
            'Your request to join the group "Submitters" has been accepted. '
            "You are now a member of the group." in sent_mail.body
        )
        assert (
            'Your request to join the group "Submitters" has been accepted. '
            "You are now a member of the group." in sent_mail.html
        )


def test_group_membership_notifications_declined(
    app,
    users,
    requests_service,
    administration_role,
    submitters_role,
    add_user_in_role,
):
    """Submit and decline a group membership request; check notification emails."""
    mail = app.extensions.get("mail")
    assert mail

    requester = users[0]
    administrator = users[1]
    add_user_in_role(administrator, administration_role)

    create_response = requests_service.create(
        requester.identity,
        data={"payload": {"justification": ""}},
        request_type="group_membership",
        topic=submitters_role,
    )

    with mail.record_messages() as outbox:
        submit_response = requests_service.execute_action(
            requester.identity, id_=create_response["id"], action="submit"
        )
        # the administrator (member of the "administration" group) is notified
        assert len(outbox) == 1
        assert outbox[0].recipients == [administrator.email]

    with mail.record_messages() as outbox:
        requests_service.execute_action(administrator.identity, id_=submit_response["id"], action="decline")
        # the requester is notified that their request was declined
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert sent_mail.recipients == [requester.email]
        assert "Your request to join group 'Submitters' was declined" in sent_mail.subject
        assert 'Your request to join the group "Submitters" was declined' in sent_mail.body
        assert 'Your request to join the group "Submitters" was declined' in sent_mail.html
