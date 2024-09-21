from invenio_requests.records.api import RequestEvent
from thesis.records.api import ThesisDraft

from oarepo_requests.types.events.topic_update import TopicUpdateEventType

from .utils import link_api2testclient


def _check_publish_topic_update(creator_client, urls, record, before_update_response):
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
        topic_updated_events[0]["payload"]["old_topic"] == f"thesis_draft.{record_id}"
    )
    assert topic_updated_events[0]["payload"]["new_topic"] == f"thesis.{record_id}"


def test_publish(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client)
    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    publish = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )
    _check_publish_topic_update(creator_client, urls, record, resp_request_create)


def test_cascade_update(
    vocab_cf,
    logged_client,
    users,
    urls,
    publish_request_data_function,
    another_topic_updating_request_function,
    create_draft_via_resource,
    search_clear,
):
    creator = users[0]
    receiver = users[1]

    creator_client = logged_client(creator)
    receiver_client = logged_client(receiver)

    draft1 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")
    draft2 = create_draft_via_resource(creator_client, custom_workflow="cascade_update")

    publish_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft1.json["id"]),
    )
    another_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=another_topic_updating_request_function(draft1.json["id"]),
    )
    publish_request_on_second_draft = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=publish_request_data_function(draft2.json["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(publish_request_create.json["links"]["actions"]["submit"]),
    )
    record = receiver_client.get(
        f"{urls['BASE_URL']}{draft1.json['id']}/draft?expand=true"
    )
    publish = receiver_client.post(
        link_api2testclient(
            record.json["expanded"]["requests"][0]["links"]["actions"]["accept"]
        ),
    )

    _check_publish_topic_update(creator_client, urls, record, publish_request_create)
    _check_publish_topic_update(creator_client, urls, record, another_request_create)

    second_draft_request = creator_client.get(
        f"{urls['BASE_URL_REQUESTS']}{publish_request_on_second_draft.json['id']}"
    )
    assert second_draft_request.json["topic"] == {
        "thesis_draft": draft2.json["id"]
    }  # check request on the other draft is unchanged


def test_edit(
    vocab_cf,
    logged_client,
    users,
    urls,
    edit_record_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    id_ = record1["id"]

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=edit_record_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json

    assert request["topic"] == {"thesis_draft": id_}


def test_new_version(
    vocab_cf,
    logged_client,
    users,
    urls,
    new_version_data_function,
    record_factory,
    search_clear,
):
    creator = users[0]
    creator_client = logged_client(creator)

    record1 = record_factory(creator.identity)
    id_ = record1["id"]

    resp_request_create = creator_client.post(
        urls["BASE_URL_REQUESTS"],
        json=new_version_data_function(record1["id"]),
    )
    resp_request_submit = creator_client.post(
        link_api2testclient(resp_request_create.json["links"]["actions"]["submit"]),
    )
    # is request accepted and closed?
    request = creator_client.get(
        f'{urls["BASE_URL_REQUESTS"]}{resp_request_create.json["id"]}',
    ).json
    ThesisDraft.index.refresh()
    new_draft_id = creator_client.get(f"/user{urls['BASE_URL']}").json["hits"]["hits"][
        0
    ]["id"]
    assert new_draft_id != id_
    assert request["topic"] == {"thesis_draft": new_draft_id}
