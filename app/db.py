import pymongo

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

def update_chain_document(nodes: list[dict]) -> None:
    """Update the nodes array in the chain document"""
    collection.update_one(
        {"_id": CHAIN_DOC_ID},
        {"$set": {"nodes": nodes}},
        upsert=True
    )
