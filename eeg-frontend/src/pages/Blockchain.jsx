import { useEffect, useState } from "react";
import { listChains, getChain } from "../api";

export default function Blockchain() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [chain, setChain] = useState(null);

  useEffect(() => {
    listChains().then(setUsers);
  }, []);

  useEffect(() => {
    if (selectedUser) {
      getChain(selectedUser).then(setChain);
    }
  }, [selectedUser]);

  return (
    <div style={{ padding: 20 }}>
      <h2>Blockchain Visualizer</h2>
      <select value={selectedUser} onChange={e=>setSelectedUser(e.target.value)}>
        <option value="">Select user</option>
        {users.map(u => <option key={u._id} value={u._id}>{u.first_name} {u.last_name}</option>)}
      </select>

      {chain && (
        <div style={{ marginTop: 20 }}>
          <h3>Chain for {chain.first_name} {chain.last_name}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {chain.nodes.map((n, i) => (
              <div key={i} style={{ padding: 10, border: "2px solid #0f4c75", borderRadius: 8, background: "#bbe1fa" }}>
                <strong>Node {i+1}</strong>
                <div>Hash: {n.hash}</div>
                <div>Prev: {n.previous_hash}</div>
                <div>Data: {JSON.stringify(n.state_data).slice(0,50)}...</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
