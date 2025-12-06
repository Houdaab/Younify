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
# DB Methods
# ------------------------
def get_last_node() -> dict | None:
    """Get the most recent node in the chain"""
    return collection.find_one(sort=[("_id", pymongo.DESCENDING)])

def insert_node(node_dict: dict) -> None:
    """Insert a node dict into MongoDB"""
    collection.insert_one(node_dict)

def get_all_nodes() -> list[dict]:
    """Get all nodes in chronological order"""
    return list(collection.find().sort("timestamp", pymongo.ASCENDING))
