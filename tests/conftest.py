import asyncio
import types
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

from server.main import app


class _InsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class _FakeCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = docs

    async def to_list(self, length: Optional[int] = None):
        return list(self._docs if length is None else self._docs[:length])


class FakeCollection:
    def __init__(self):
        self._docs: List[Dict[str, Any]] = []

    async def insert_one(self, doc: Dict[str, Any]):
        # ensure _id exists
        if "_id" not in doc:
            # simple string id
            doc["_id"] = f"fake_{len(self._docs)+1}"
        self._docs.append(doc)
        return _InsertOneResult(doc["_id"])

    def find(self, query: Optional[Dict[str, Any]] = None, projection: Optional[Dict[str, int]] = None):
        # minimal $in/_id or empty filter handling
        if not query:
            return _FakeCursor(self._docs)
        docs = self._docs
        if "_id" in query and isinstance(query["_id"], dict) and "$in" in query["_id"]:
            ids = set(query["_id"]["$in"])
            docs = [d for d in docs if d.get("_id") in ids]
        # simple equality filters
        else:
            def match(d: Dict[str, Any]) -> bool:
                for k, v in query.items():
                    if d.get(k) != v:
                        return False
                return True
            docs = [d for d in docs if match(d)]
        if projection:
            proj_docs = []
            include = {k for k, v in projection.items() if v}
            for d in docs:
                proj_docs.append({k: d.get(k) for k in include if k in d})
            docs = proj_docs
        return _FakeCursor(docs)

    async def find_one(self, query: Dict[str, Any]):
        cursor = self.find(query)
        docs = await cursor.to_list()
        return docs[0] if docs else None

    async def create_index(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def _app_overrides(monkeypatch):
    """Override DB and external dependencies for all tests."""
    # Fake DB collections by name
    collections: Dict[str, FakeCollection] = {
        "generated_content": FakeCollection(),
        "content": FakeCollection(),
        "users": FakeCollection(),
        "question_sets": FakeCollection(),
        "answers": FakeCollection(),
        "feedback": FakeCollection(),
    }

    def fake_col(name: str):
        try:
            return collections[name]
        except KeyError:
            c = FakeCollection()
            collections[name] = c
            return c

    # Patch col() used in routers, vector, and database module to avoid real DB
    monkeypatch.setattr("server.routers.content.col", fake_col, raising=True)
    monkeypatch.setattr("server.database.col", fake_col, raising=True)
    monkeypatch.setattr("server.vector.col", fake_col, raising=False)
    # Optional: if other routers tested, add their patches too
    # monkeypatch.setattr("server.routers.questions.col", fake_col, raising=False)
    # monkeypatch.setattr("server.routers.answers.col", fake_col, raising=False)

    # Quota: no-op
    async def no_quota(*args, **kwargs):
        return None

    monkeypatch.setattr("server.plan.ensure_content_quota", no_quota, raising=False)
    monkeypatch.setattr("server.plan.record_content_generation", no_quota, raising=False)
    # Patch symbols imported into content router module directly
    monkeypatch.setattr("server.routers.content.ensure_content_quota", no_quota, raising=False)
    monkeypatch.setattr("server.routers.content.record_content_generation", no_quota, raising=False)

    # Content generator: deterministic content
    def fake_generate_content(self, topic: str, difficulty: str, subject: str, content_type: str, learning_objectives: list[str]):
        return {
            "content": f"[GEN:{subject}:{difficulty}:{content_type}] Topic: {topic}\nKey points...",
            "key_concepts": ["concept1", "concept2"],
            "sources": ["https://example.com"],
        }

    monkeypatch.setattr(
        "agents.content_generator.ContentGeneratorAgent.generate_content",
        fake_generate_content,
        raising=True,
    )

    # Vector index: disable for determinism in basic tests
    monkeypatch.setattr("server.vector.has_index", lambda: False, raising=False)
    monkeypatch.setattr("server.vector.search_similar", lambda text, k=5: ([], []), raising=False)
    monkeypatch.setattr("server.vector.add_to_index", lambda *args, **kwargs: None, raising=False)

    # Disable startup DB init and vector build to prevent connection attempts
    async def _noop_async(*args, **kwargs):
        return None

    monkeypatch.setattr("server.main.init_db", _noop_async, raising=False)
    monkeypatch.setattr("server.main.close_db", _noop_async, raising=False)
    monkeypatch.setattr("server.main.build_vector_index", _noop_async, raising=False)

    # Auth override
    from server import auth
    app.dependency_overrides[auth.get_current_user] = lambda: {"sub": "test-user"}

    yield

    # cleanup overrides
    app.dependency_overrides = {}


@pytest.fixture()
def client(_app_overrides):
    return TestClient(app)
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
