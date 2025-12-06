import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ValidationError

from app.db import get_chain_by_id, update_chain_document


# ------------------------
# Pydantic Models
# ------------------------

class BrainStateNodeModel(BaseModel):
    state_data: str = Field(..., description="Comma separated brain data")
    previous_hash: str
    hash: str
    timestamp: str


class UpdateChainRequest(BaseModel):
    # Only NEW incoming state data (1 item)
    state_data: str = Field(..., description="New brain state data")

    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]] = None
    nodes: Optional[List[BrainStateNodeModel]] = None


# ------------------------
# Blockchain Node
# ------------------------

class BrainStateNode:
    def __init__(self, state_data: str, previous_hash: str = ""):
        self.state_data = state_data
        self.previous_hash = previous_hash
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
            "timestamp": self.timestamp
        }

# ------------------------
# Blockchain Functions
# ------------------------

def add_brain_state(chain_update: UpdateChainRequest, doc_id: str) -> dict:
    """Add a new brain state to the single-chain document"""

    chain_doc = get_chain_by_id(doc_id)
    nodes = chain_doc.get("nodes", [])

    # Last node hash or genesis
    previous_hash = nodes[-1]["hash"] if nodes else ""

    # Create new blockchain node
    node = BrainStateNode(chain_update.state_data, previous_hash)
    nodes.append(node.to_dict())

    # Validate all nodes with Pydantic
    validated_nodes = [BrainStateNodeModel(**n) for n in nodes]

    # Update the database: pass validated nodes + metadata
    update_chain_document(validated_nodes, chain_update)

    return node.to_dict()


def verify_chain(chain_id: str) -> bool:
    """Verify full chain integrity from database"""

    doc = get_chain_by_id(chain_id)
    nodes = doc.get("nodes", [])

    try:
        validated_nodes = [BrainStateNodeModel(**n) for n in nodes]
    except ValidationError as e:
        print("Validation error:", e)
        return False

    for i in range(1, len(validated_nodes)):

        prev_node = validated_nodes[i - 1]
        node = validated_nodes[i]

        if node.previous_hash != prev_node.hash:
            print(f"Hash mismatch at node {i}")
            return False

        recalculated_hash = hashlib.sha256(
            (node.state_data + node.previous_hash + node.timestamp).encode("utf-8")
        ).hexdigest()

        if node.hash != recalculated_hash:
            print(f"Invalid hash at node {i}")
            return False

    return True


# ------------------------
# Example Usage (FIXED)
# ------------------------
#
# if __name__ == "__main__":
    # brain_states = [
    #     "0,1,1,0,1,0,0,1",
    #     "0,1,1,1,1,0,1,0",
    #     "1,0,1,0,0,1,0,1",
    # ]
    #
    # for state in brain_states:
    #
    #     req = UpdateChainRequest(
    #         state_data=state,
    #         first_name="Aliaksandr",
    #         last_name="Husakou",
    #         gender="male"
    #     )
    #
    #     node = add_brain_state(req)
    #     print(f"Added node: {node['hash']}")

    # print("Blockchain valid?", verify_chain())
