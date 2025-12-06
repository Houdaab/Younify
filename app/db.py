import uuid
from typing import Optional, Literal, List

import pymongo

from app.models.internal import BrainStateNodeModel, ExtraUserData

# ------------------------
# MongoDB Setup
# ------------------------
MONGO_URI = "mongodb://admin:secret@localhost:27017/?authSource=admin"
DB_NAME = "brain_chain_db"
COLLECTION_NAME = "brain_states"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

videos_col = db["videos"]     # stores uploaded videos

# -----------------------------

# Videos collection: index on user_id for fast lookup and on uploaded_at for sorting
videos_col.create_index([("user_id", pymongo.ASCENDING)])
videos_col.create_index([("uploaded_at", pymongo.ASCENDING)])


def create_new_chain(first_name: Optional[str] = None,
                     last_name: Optional[str] = None,
                     gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None) -> dict:
    """Create a new empty chain document and return summary"""

    new_id = str(uuid.uuid4())

    doc = {
        "_id": new_id,
        "nodes": [],
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "is_human": False,
    }

    collection.insert_one(doc)

    # Return summary without nodes
    return {
        "_id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "is_human": False,
        "nodes_count": 0
    }


def update_chain_is_human(chain_id: str, is_human: bool) -> None:
    """
    Update only the is_human field (and optional score) for a specific chain.

    Returns
    -------
    None
    """

    update_data = {"is_human": is_human}

    result = collection.update_one(
        {"_id": chain_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise ValueError(f"Chain with id '{chain_id}' not found")


def update_chain_document(
    chain_id: str,
    nodes: list[BrainStateNodeModel],
    meta: ExtraUserData
) -> None:
    """Update the specified chain document with nodes and optional user info"""

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
        {"_id": chain_id},
        {"$set": update_data},
        upsert=True
    )


def list_chain_summaries() -> List[dict]:
    """
    Return a summary of all chain documents (_id + user info + nodes_count)
    """
    docs = collection.find({}, {"nodes": 1, "first_name": 1, "last_name": 1, "gender": 1})
    summaries = []
    for doc in docs:
        summaries.append({
            "_id": doc["_id"],
            "first_name": doc.get("first_name"),
            "last_name": doc.get("last_name"),
            "gender": doc.get("gender"),
            "nodes_count": len(doc.get("nodes", []))
        })
    return summaries


def get_chain_by_id(chain_id: str) -> Optional[dict]:
    """Return the full chain document by _id"""
    doc = collection.find_one({"_id": chain_id})
    return doc  # Returns None if not found


def add_node_to_chain(chain_id: str, node: BrainStateNodeModel,
                      first_name: Optional[str] = None,
                      last_name: Optional[str] = None,
                      gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None
                      ) -> BrainStateNodeModel:
    """Add a new node to the chain and update user info if provided"""
    doc = get_chain_by_id(chain_id)
    if doc["_id"] != chain_id:
        raise ValueError("Chain not found")

    nodes = doc.get("nodes", [])
    nodes.append(node.model_dump())

    nodes = [BrainStateNodeModel(**n) for n in nodes]

    update_data = ExtraUserData(
        first_name=first_name,
        last_name=last_name,
        gender=gender
    )

    update_chain_document(chain_id, nodes, update_data)
    return node
