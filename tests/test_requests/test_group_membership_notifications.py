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
from invenio_access.permissions import system_identity
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
        data={"payload": {"justification": "I need to submit datasets for my research group."}},
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
        assert "I need to submit datasets for my research group." in sent_mail.body
        assert "I need to submit datasets for my research group." in sent_mail.html

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
        data={"payload": {"justification": "I need to submit datasets for my research group."}},
        request_type="group_membership",
        topic=submitters_role,
    )

    with mail.record_messages() as outbox:
        submit_response = requests_service.execute_action(
            requester.identity, id_=create_response["id"], action="submit"
        )
        # the administrator (member of the "administration" group) is notified
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert sent_mail.recipients == [administrator.email]
        assert "I need to submit datasets for my research group." in sent_mail.body

    with mail.record_messages() as outbox:
        requests_service.execute_action(administrator.identity, id_=submit_response["id"], action="decline")
        # the requester is notified that their request was declined
        assert len(outbox) == 1
        sent_mail = outbox[0]
        assert sent_mail.recipients == [requester.email]
        assert "Your request to join group 'Submitters' was declined" in sent_mail.subject
        assert 'Your request to join the group "Submitters" was declined' in sent_mail.body
        assert 'Your request to join the group "Submitters" was declined' in sent_mail.html


def test_group_membership_stateful_name_and_description(
    users,
    requests_service,
    administration_role,
    submitters_role,
    add_user_in_role,
):
    """Check stateful_name/stateful_description texts for the group_membership request type."""
    requester = users[0]
    administrator = users[1]
    other = users[2]
    add_user_in_role(administrator, administration_role)

    # resolved topic, as used elsewhere (notifications, UI) - a dict with the group's description/name
    topic = current_groups_service.read(system_identity, submitters_role.id).to_dict()

    create_response = requests_service.create(
        requester.identity,
        data={"payload": {"justification": "I need to submit datasets for my research group."}},
        request_type="group_membership",
        topic=submitters_role,
    )
    request = create_response._request  # noqa: SLF001
    request_type = request.type

    # no request created yet
    assert (
        request_type.stateful_name(requester.identity, topic=topic, request=None)
        == "Request membership in group 'Submitters'"
    )
    assert (
        request_type.stateful_description(requester.identity, topic=topic, request=None)
        == "Request membership in group 'Submitters'. You will be notified about the decision by email."
    )

    # request created but not yet submitted
    assert (
        request_type.stateful_name(requester.identity, topic=topic, request=request)
        == "Request membership in group 'Submitters'"
    )
    assert (
        request_type.stateful_description(requester.identity, topic=topic, request=request)
        == "Submit request to join group 'Submitters'."
    )
    # the administrator can manage group membership in general, but there's nothing
    # for them to act on yet since the request hasn't been submitted
    assert (
        request_type.stateful_description(administrator.identity, topic=topic, request=request)
        == "This request for membership in group 'Submitters' has not yet been submitted."
    )

    submit_response = requests_service.execute_action(requester.identity, id_=create_response["id"], action="submit")
    submitted_request = submit_response._request  # noqa: SLF001

    # submitted: as the requester
    assert (
        request_type.stateful_name(requester.identity, topic=topic, request=submitted_request)
        == "Membership in group 'Submitters' requested"
    )
    assert (
        request_type.stateful_description(requester.identity, topic=topic, request=submitted_request)
        == "Membership in group 'Submitters' requested. You will be notified about the decision by email."
    )

    # submitted: as the administrator (receiver)
    assert (
        request_type.stateful_name(administrator.identity, topic=topic, request=submitted_request)
        == "Membership in group 'Submitters' requested"
    )
    assert (
        request_type.stateful_description(administrator.identity, topic=topic, request=submitted_request)
        == "You have been asked to approve the request for membership in group 'Submitters'. "
        "You can approve or reject the request."
    )

    # submitted: as an unrelated user
    assert (
        request_type.stateful_description(other.identity, topic=topic, request=submitted_request)
        == "Membership in group 'Submitters' requested."
    )
