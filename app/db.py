from typing import Optional, Literal, List

import pymongo

from app.models.internal import BrainStateNodeModel, UpdateChainRequest

# ------------------------
# MongoDB Setup
# ------------------------
MONGO_URI = "mongodb://admin:secret@localhost:27017/?authSource=admin"
DB_NAME = "brain_chain_db"
COLLECTION_NAME = "brain_states"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ------------------------
# DB Methods for single chain document
# ------------------------
CHAIN_DOC_ID = "brain_chain_main"  # fixed _id for single document

def get_chain_document() -> dict:
    """Get the single chain document, create if not exists"""
    doc = collection.find_one({"_id": CHAIN_DOC_ID})
    if not doc:
        doc = {"_id": CHAIN_DOC_ID, "nodes": []}
        collection.insert_one(doc)
    return doc


def update_chain_document(nodes: list[BrainStateNodeModel], meta: UpdateChainRequest) -> None:
    """Update the single chain document with nodes and optional user info"""

    update_data = {
        "nodes": [n.model_dump() for n in nodes]
    }

    if meta.first_name is not None:
        update_data["first_name"] = meta.first_name

    if meta.last_name is not None:
        update_data["last_name"] = meta.last_name

    if meta.gender is not None:
        update_data["gender"] = meta.gender

    collection.update_one(
        {"_id": CHAIN_DOC_ID},
        {"$set": update_data},
        upsert=True
    )


def list_chain_summaries() -> List[dict]:
    """
    Return a summary of all chains (_id + user info + nodes count)
    """
    doc = get_chain_document()
    summary = {
        "_id": doc["_id"],
        "first_name": doc.get("first_name"),
        "last_name": doc.get("last_name"),
        "gender": doc.get("gender"),
        "nodes_count": len(doc.get("nodes", [])),
    }
    return [summary]


def get_chain_by_id(chain_id: str) -> dict:
    """Return the full chain document by _id"""
    doc = get_chain_document()
    if doc["_id"] != chain_id:
        return None
    return doc


def add_node_to_chain(chain_id: str, node: BrainStateNodeModel,
                      first_name: Optional[str] = None,
                      last_name: Optional[str] = None,
                      gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None
                      ) -> BrainStateNodeModel:
    """Add a new node to the chain and update user info if provided"""
    doc = get_chain_document()
    if doc["_id"] != chain_id:
        raise ValueError("Chain not found")

    nodes = doc.get("nodes", [])
    nodes.append(node.model_dump())

    nodes = [BrainStateNodeModel(**n) for n in nodes]

    update_data = UpdateChainRequest(
        first_name=first_name,
        last_name=last_name,
        gender=gender
    )

    update_chain_document(nodes, update_data)
    return node
