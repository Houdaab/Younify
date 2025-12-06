import hashlib
from datetime import datetime, timezone
from db import get_chain_document, update_chain_document

# ------------------------
# Blockchain Node
# ------------------------
class BrainStateNode:
    def __init__(self, state_data: str, previous_hash: str = ""):
        self.state_data = state_data
        self.previous_hash = previous_hash
        # Use timezone-aware UTC and ISO format
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        sha = hashlib.sha256()
        sha.update(self.state_data.encode("utf-8"))
        sha.update(self.previous_hash.encode("utf-8"))
        sha.update(self.timestamp.encode("utf-8"))
        return sha.hexdigest()

    def to_dict(self) -> dict:
        return {
            "state_data": self.state_data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }

# ------------------------
# Blockchain Functions
# ------------------------
def add_brain_state(state_data: str) -> dict:
    """Add a new node to the single-chain document"""
    chain_doc = get_chain_document()
    nodes = chain_doc["nodes"]

    previous_hash = nodes[-1]["hash"] if nodes else ""
    node = BrainStateNode(state_data, previous_hash)
    nodes.append(node.to_dict())

    update_chain_document(nodes)
    return node.to_dict()


def verify_chain() -> bool:
    nodes = get_chain_document()["nodes"]
    for i in range(1, len(nodes)):
        prev_node = nodes[i - 1]
        node = nodes[i]

        # Convert timestamp to string if it's a datetime (legacy nodes)
        timestamp_str = (
            node["timestamp"].isoformat()
            if isinstance(node["timestamp"], datetime)
            else node["timestamp"]
        )

        if node["previous_hash"] != prev_node["hash"]:
            print(f"Hash mismatch at node {i}")
            return False

        recalculated_hash = hashlib.sha256(
            (node["state_data"] + node["previous_hash"] + timestamp_str).encode("utf-8")
        ).hexdigest()

        if node["hash"] != recalculated_hash:
            print(f"Invalid hash at node {i}")
            return False

    return True


# ------------------------
# Example Usage
# ------------------------
if __name__ == "__main__":
    brain_states = [
        "0,1,1,0,1,0,0,1",
        "0,1,1,1,1,0,1,0",
        "1,0,1,0,0,1,0,1",
    ]

    for state in brain_states:
        node = add_brain_state(state)
        print(f"Added node: {node['hash']}")

    print("Blockchain valid?", verify_chain())
