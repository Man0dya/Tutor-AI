"""
Backfill embeddings for existing generated_content documents to support Atlas Vector Search.

Run this once after enabling Atlas Search to populate 'similarity_embedding' and 'content_embedding'.

Usage (from repo root):
  python -m utils.backfill_embeddings
"""
from __future__ import annotations

import asyncio
from typing import List

from server.config import MONGODB_URI, MONGODB_DB
from utils.embedding import embed_texts

import motor.motor_asyncio

BATCH = 64


async def main():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB]
    gc = db["generated_content"]

    cursor = gc.find({
        "$or": [
            {"similarity_embedding": {"$exists": False}},
            {"content_embedding": {"$exists": False}},
        ]
    }, {"_id": 1, "similarity_basis": 1, "content": 1}).batch_size(BATCH)

    docs: List[dict] = await cursor.to_list(length=None)
    print(f"Found {len(docs)} docs to backfill")

    for i in range(0, len(docs), BATCH):
        chunk = docs[i:i+BATCH]
        sim_texts = [d.get("similarity_basis") or d.get("topic") or "" for d in chunk]
        cnt_texts = [d.get("content") or "" for d in chunk]

        try:
            sim_vecs = embed_texts(sim_texts).tolist()
        except Exception:
            sim_vecs = [None for _ in chunk]
        try:
            cnt_vecs = embed_texts(cnt_texts).tolist()
        except Exception:
            cnt_vecs = [None for _ in chunk]

        from pymongo import UpdateOne
        bulk = []
        for d, svec, cvec in zip(chunk, sim_vecs, cnt_vecs):
            update = {"$set": {}}
            if svec is not None:
                update["$set"]["similarity_embedding"] = svec
            if cvec is not None:
                update["$set"]["content_embedding"] = cvec
            if update["$set"]:
                bulk.append(UpdateOne({"_id": d["_id"]}, update))
        if bulk:
            await gc.bulk_write(bulk, ordered=False)
        print(f"Updated {len(bulk)} docs in batch {i//BATCH + 1}")

    print("Backfill complete")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
