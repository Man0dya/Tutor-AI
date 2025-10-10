import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server import auth


class FakeCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = docs

    async def to_list(self, length: Optional[int] = None):
        return list(self._docs)


class FakeCollection:
    def __init__(self):
        self.docs: List[Dict[str, Any]] = []

    async def insert_one(self, doc: Dict[str, Any]):
        # Assign _id if missing (like generated_content)
        if "_id" not in doc:
            try:
                from bson import ObjectId
                doc["_id"] = ObjectId()
            except Exception:
                doc["_id"] = f"fake_{len(self.docs)+1}"
        self.docs.append(doc)
        return SimpleNamespace(inserted_id=doc["_id"])

    def find(self, filter: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None):
        if not filter:
            return FakeCursor(self.docs)
        # Minimal filter support: {"_id": {"$in": [...]}} or equality on simple fields
        results = self.docs
        for k, v in filter.items():
            if isinstance(v, dict) and "$in" in v:
                allowed = set(v["$in"])  # keep as-is (ObjectId or str)
                results = [d for d in results if d.get(k) in allowed]
            else:
                results = [d for d in results if d.get(k) == v]
        return FakeCursor(results)


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # Override auth to return a static user
    app.dependency_overrides[auth.get_current_user] = lambda: {"sub": "test-user"}

    # In-memory collections
    content_col = FakeCollection()
    generated_col = FakeCollection()

    # col(name) resolver
    def fake_col(name: str):
        if name == "content":
            return content_col
        if name == "generated_content":
            return generated_col
        # default separate collection
        return FakeCollection()

    # Patch DB accessor in content router only (we test content endpoints here)
    import server.routers.content as content_router
    monkeypatch.setattr(content_router, "col", fake_col, raising=True)

    # Disable quota writes
    import server.plan as plan
    monkeypatch.setattr(plan, "ensure_content_quota", lambda user_id: asyncio.sleep(0), raising=True)
    monkeypatch.setattr(plan, "record_content_generation", lambda user_id: asyncio.sleep(0), raising=True)

    # Stub content generation agent for determinism
    import agents.content_generator as content_agent_mod

    class StubAgent:
        def generate_content(self, topic: str, difficulty: str, subject: str, content_type: str, learning_objectives: List[str]):
            return {
                "content": f"Generated content for: {topic}\nSubject: {subject} | Difficulty: {difficulty} | Type: {content_type}",
                "key_concepts": ["concept1", "concept2"],
            }

    monkeypatch.setattr(content_agent_mod, "ContentGeneratorAgent", StubAgent, raising=True)

    # Ensure vector index is not used for tests unless we explicitly test it
    import server.vector as vector
    monkeypatch.setattr(vector, "has_index", lambda: False, raising=True)
    monkeypatch.setattr(vector, "search_similar", lambda text, k=5: ([], []), raising=True)
    monkeypatch.setattr(content_router, "has_index", lambda: False, raising=True)
    monkeypatch.setattr(content_router, "search_similar", lambda text, k=5: ([], []), raising=True)

    yield

    # Cleanup overrides
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    return TestClient(app)
