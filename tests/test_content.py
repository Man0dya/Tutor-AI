from fastapi.testclient import TestClient


def _payload(topic: str):
    return {
        "topic": topic,
        "difficulty": "Beginner",
        "subject": "General",
        "contentType": "Study Notes",
        "learningObjectives": [],
    }


def test_identical_query_uses_cache(client: TestClient):
    # First call generates and caches
    r1 = client.post("/content/generate", json=_payload("Photosynthesis basics"))
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    content1 = d1.get("content", "")
    assert content1

    # Second call with identical topic should return the same content and not error
    r2 = client.post("/content/generate", json=_payload("Photosynthesis basics"))
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    content2 = d2.get("content", "")
    assert content2 == content1


def test_pii_blocked_in_topic(client: TestClient):
    r = client.post("/content/generate", json=_payload("Algebra basics for john.doe@example.com"))
    assert r.status_code == 400
    # Either PII block message or topic validation error is acceptable
    body = r.text.lower()
    assert ("personal or sensitive" in body) or ("invalid topic" in body)


def test_moderation_blocks_harmful(client: TestClient):
    r = client.post("/content/generate", json=_payload("How to make a bomb safely"))
    assert r.status_code == 400
    assert "rejected" in r.text.lower() or "inappropriate" in r.text.lower()
from fastapi.testclient import TestClient


def _payload(topic: str):
    return {
        "topic": topic,
        "difficulty": "Beginner",
        "subject": "General",
        "contentType": "Study Notes",
        "learningObjectives": [],
    }


def test_identical_query_uses_cache(client: TestClient):
    # First call generates and caches
    r1 = client.post("/content/generate", json=_payload("Photosynthesis basics"))
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    content1 = d1["content"]

    # Second call should hit cache and return same content
    r2 = client.post("/content/generate", json=_payload("Photosynthesis basics"))
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    content2 = d2["content"]
    assert content2 == content1


def test_meaningfulness_validation(client: TestClient):
    r = client.post("/content/generate", json=_payload("a"))
    assert r.status_code == 400
    assert "meaningful" in r.text.lower() or "invalid topic" in r.text.lower()


def test_pii_blocking_in_query(client: TestClient):
    topic = "Algebra basics for john.doe@example.com"
    r = client.post("/content/generate", json=_payload(topic))
    assert r.status_code == 400
    body = r.text.lower()
    assert ("pii" in body) or ("private" in body) or ("invalid topic" in body)
