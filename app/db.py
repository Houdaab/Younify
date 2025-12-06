import pymongo

from app.models import UpdateChainRequest, BrainStateNodeModel

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