import hashlib
from datetime import datetime
from db import get_last_node, insert_node, get_all_nodes

# ------------------------
# Blockchain Node
# ------------------------
class BrainStateNode:
    def __init__(self, state_data: str, previous_hash: str = ""):
        """
        state_data: long string of numbers and commas
        previous_hash: hash of previous node in the chain
        """
        self.state_data = state_data
        self.previous_hash = previous_hash
        self.timestamp = datetime.utcnow()
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of this node"""
        sha = hashlib.sha256()
        sha.update(self.state_data.encode("utf-8"))
        sha.update(self.previous_hash.encode("utf-8"))
        sha.update(str(self.timestamp).encode("utf-8"))
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
    """Add a new brain state node to the blockchain"""
    last_node = get_last_node()
    previous_hash = last_node["hash"] if last_node else ""
    node = BrainStateNode(state_data, previous_hash)
    insert_node(node.to_dict())
    return node.to_dict()

def verify_chain() -> bool:
    """Verify the integrity of the blockchain"""
    nodes = get_all_nodes()
    for i in range(1, len(nodes)):
        prev_node = nodes[i - 1]
        node = nodes[i]
        # Check hash chain
        if node["previous_hash"] != prev_node["hash"]:
            print(f"Hash mismatch at node {i}")
            return False
        # Check node hash is correct
        recalculated_hash = hashlib.sha256(
            (node["state_data"] + node["previous_hash"] + str(node["timestamp"])).encode("utf-8")
        ).hexdigest()
        if node["hash"] != recalculated_hash:
            print(f"Invalid hash at node {i}")
            return False
    return True

# ------------------------
# Example Usage
# ------------------------
if __name__ == "__main__":
    # Example brain states
    brain_states = [
        "0,1,1,0,1,0,0,1",
        "0,1,1,1,1,0,1,0",
        "1,0,1,0,0,1,0,1",
    ]

    for state in brain_states:
        node = add_brain_state(state)
        print(f"Added node: {node['hash']}")

    print("Blockchain valid?", verify_chain())
