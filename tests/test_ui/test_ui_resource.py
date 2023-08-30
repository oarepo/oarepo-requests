
"""
def test_ui_resource_create_new(app, record_ui_resource, record_service):
    assert record_ui_resource.empty_record(None) == {"title": None}


def test_ui_resource_form_config(app, record_ui_resource):
    # TODO: what is this?
    assert record_ui_resource


def test_draft_publish_request_present(
        app, record_ui_resource, example_topic_draft, client_with_login, fake_manifest
):
    with client_with_login.get(f"/thesis/{example_topic_draft['id']}/draft") as c:
        assert c.status_code == 200
        assert "delete_record: " in c.text
        assert "&#39;type&#39;: &#39;delete_record&#39" in c.text
        assert "&#39;receiver&#39;: None" in c.text
        assert "&#39;status&#39;: &#39;created&#39;" in c.text
        assert "&#39;links&#39;: {}" in c.text
"""


def test_record_delete_request_present(
    app, record_ui_resource, example_topic, client_with_login, fake_manifest
):
    with client_with_login.get(f"/thesis/{example_topic['id']}") as c:
        assert c.status_code == 200
        assert "delete_record: " in c.text
        assert "&#39;type&#39;: &#39;delete_record&#39" in c.text
        assert "&#39;receiver&#39;: None" in c.text
        assert "&#39;status&#39;: &#39;created&#39;" in c.text
        assert "&#39;links&#39;: {}" in c.text


"""
def test_permissions_on_search(
    app, record_ui_resource, simple_record, client, fake_manifest
):
    with client.get(f"/simple-model/") as c:
        assert c.status_code == 200
        assert ("permissions={&#39;can_create&#39;: True}") in c.text


def test_ui_links_on_detail(
    app, record_ui_resource, simple_record, client, fake_manifest
):
    with client.get(f"/simple-model/{simple_record.id}") as c:
        assert c.status_code == 200
        assert (
            f"self:https://127.0.0.1:5000/simple-model/{simple_record.id}\n" in c.text
        )
        assert (
            f"edit:https://127.0.0.1:5000/simple-model/{simple_record.id}/edit\n"
            in c.text
        )


def test_ui_listing(app, record_ui_resource, simple_record, client, fake_manifest):
    with client.get(f"/simple-model/") as c:
        assert c.status_code == 200
        assert "self:https://127.0.0.1:5000/simple-model" in c.text
        assert "next:https://127.0.0.1:5000/simple-model?page=2" in c.text
        assert "create:https://127.0.0.1:5000/simple-model/_new" in c.text

    with client.get(f"/simple-model/?page=2") as c:
        assert c.status_code == 200
        assert "self:https://127.0.0.1:5000/simple-model?page=2" in c.text
        assert "prev:https://127.0.0.1:5000/simple-model?page=1" in c.text
        assert "next:https://127.0.0.1:5000/simple-model?page=3" in c.text
        assert "create:https://127.0.0.1:5000/simple-model/_new" in c.text


def test_service_ui_link(app, record_service, example_topic, fake_manifest):
    data = record_service.read(system_identity, example_topic.id)
    # note: in tests, the ui and api urls are the same, this should be different
    # in production
    assert (
        data.links["self"]
        == f"https://127.0.0.1:5000/api/simple-model/{example_topic.id}"
    )
    assert data.links["ui"] == f"https://127.0.0.1:5000/simple-model/{example_topic.id}"
"""
