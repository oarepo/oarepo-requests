import pytest
from invenio_drafts_resources.services import (
    RecordServiceConfig as InvenioRecordDraftsServiceConfig,
)
from oarepo_runtime.services.config.service import PermissionsPresetsConfigMixin
from thesis.records.api import ThesisDraft, ThesisRecord
from thesis.services.records.config import ThesisServiceConfig

from oarepo_requests.errors import OpenRequestAlreadyExists

from .utils import BASE_URL, BASE_URL_REQUESTS, link_api2testclient
from invenio_requests.records.api import Request


def data(receiver, record):
    return {
        "receiver": {"user": receiver.id},
        "request_type": "publish_draft",
        "topic": {"thesis_draft": record.json["id"]},
    }

"""
def test_links_in_search(client_factory, identity_simple, users):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    draft1 = creator_client.post(f"{BASE_URL}", json={})
    receiver = users[1]
    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, draft1)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )

    # test links in search
    response_search = receiver_client.get(f"user{BASE_URL}")
    links = response_search.json["hits"]["hits"][0]["links"]["requests"][
        "publish_draft"
    ]
    assert links.keys() == {"accept", "decline"}

    publish = receiver_client.post(link_api2testclient(links["accept"]))
    ThesisRecord.index.refresh()
    response_search = receiver_client.get(BASE_URL)
    print()
"""

def test_publish(client_factory, identity_simple, users, monkeypatch):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())
    receiver = users[1]

    draft1 = creator_client.post(f"{BASE_URL}", json={})
    draft2 = creator_client.post(f"{BASE_URL}", json={})
    draft3 = creator_client.post(f"{BASE_URL}", json={})
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{BASE_URL}")
    lst = creator_client.get(BASE_URL)
    assert len(draft_lst.json["hits"]["hits"]) == 3
    assert len(lst.json["hits"]["hits"]) == 0

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, draft1)
    )

    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()

    record = receiver_client.get(f"{BASE_URL}{draft1.json['id']}/draft")
    assert record.json["requests"][0]["links"]["actions"].keys() == {
        "accept",
        "decline",
    }
    publish = receiver_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["accept"])
    )
    record = receiver_client.get(f"{BASE_URL}{draft2.json['id']}/draft")
    assert "publish_draft" not in record.json["parent"]

    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    draft_lst = creator_client.get(f"/user{BASE_URL}")
    lst = creator_client.get(BASE_URL)
    assert len(draft_lst.json["hits"]["hits"]) == 2
    assert len(lst.json["hits"]["hits"]) == 1

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, draft2)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = receiver_client.get(f"{BASE_URL}{draft2.json['id']}/draft")
    decline = receiver_client.post(
        link_api2testclient(
            record.json["requests"][0]["links"]["actions"]["decline"]
        )
    )
    declined_request = creator_client.get(
        f"{BASE_URL_REQUESTS}{resp_request_create.json['id']}"
    )
    assert declined_request.json["status"] == "declined"
    record = receiver_client.get(f"{BASE_URL}{draft2.json['id']}/draft")

    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, draft3)
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    record = creator_client.get(f"{BASE_URL}{draft3.json['id']}/draft")
    assert record.json["requests"][0]["links"]["actions"].keys() == {"cancel"}
    cancel = creator_client.post(
        link_api2testclient(record.json["requests"][0]["links"]["actions"]["cancel"])
    )
    canceled_request = creator_client.get(
        f"{BASE_URL_REQUESTS}{resp_request_create.json['id']}"
    )
    assert canceled_request.json["status"] == "cancelled"

"""
def test_errors(client_factory, record_factory, identity_simple, users, monkeypatch):
    creator_client = users[0].login(client_factory())
    receiver_client = users[1].login(client_factory())

    receiver = users[1]

    def data(receiver, record):
        return {
            "receiver": {"user": receiver.id},
            "request_type": "publish_draft",
            "topic": {"thesis_draft": record.json["id"]},
        }

    draft = creator_client.post(f"{BASE_URL}", json={})
    ThesisRecord.index.refresh()
    ThesisDraft.index.refresh()
    resp_request_create = creator_client.post(
        BASE_URL_REQUESTS, json=data(receiver, draft)
    )
    creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"])
    )
    with pytest.raises(OpenRequestAlreadyExists):
        creator_client.post(BASE_URL_REQUESTS, json=data(receiver, draft))
"""

