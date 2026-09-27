def test_search_returns_all_active_resources_by_default(client):
    resp = client.get("/resources/")
    assert resp.status_code == 200
    assert b"Intro to Python" in resp.data
    assert b"Advanced Networking" in resp.data


def test_search_filters_by_free_only(client):
    resp = client.get("/resources/?free_only=1")
    assert resp.status_code == 200
    assert b"Intro to Python" in resp.data
    assert b"Advanced Networking" not in resp.data


def test_search_filters_by_difficulty(client):
    resp = client.get("/resources/?difficulty=advanced")
    assert resp.status_code == 200
    assert b"Advanced Networking" in resp.data
    assert b"Intro to Python" not in resp.data


def test_search_with_query_text(client):
    resp = client.get("/resources/?q=Python")
    assert resp.status_code == 200
    assert b"Intro to Python" in resp.data


def test_search_with_no_matches_shows_empty_state(client):
    resp = client.get("/resources/?q=NoSuchResourceAtAll")
    assert resp.status_code == 200
    assert b"No resources match" in resp.data


def test_resource_detail_shows_rating_unavailable_when_no_rating(client, app):
    from app.models import Resource
    with app.app_context():
        resource = Resource.query.filter_by(url="https://example.com/python").first()
        resource_id = resource.id
    resp = client.get(f"/resources/{resource_id}")
    assert resp.status_code == 200
    assert b"Rating unavailable" in resp.data


def test_resource_detail_404_for_missing_resource(client):
    resp = client.get("/resources/999999")
    assert resp.status_code == 404
