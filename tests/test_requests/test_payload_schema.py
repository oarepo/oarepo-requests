from oarepo_requests.types import PublishDraftRequestType


def test_publish_request_payload_schema(app, db):
    ma_schema = PublishDraftRequestType.marshmallow_schema()
    assert ma_schema().dump(
        {
            "payload": {
                "published_record:links:self": "http://localhost:5000/api/records/1"
            }
        }
    ) == {
        "payload": {
            "published_record:links:self": "http://localhost:5000/api/records/1"
        },
        "links": {},
        "title": "",
    }
