import { useState, useEffect } from "react";
import { listChains, addNode } from "../api";

export default function AddNode() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    listChains().then(setUsers);
  }, []);

  const handleSubmit = async e => {
    e.preventDefault();
    if (!selectedUser || !file) return;
    const res = await addNode(selectedUser, file);
    setMessage(`Node added with hash: ${res.hash}`);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Add Node to User</h2>
      <form onSubmit={handleSubmit}>
        <select value={selectedUser} onChange={e=>setSelectedUser(e.target.value)}>
          <option value="">Select user</option>
          {users.map(u => <option key={u._id} value={u._id}>{u.first_name} {u.last_name}</option>)}
        </select><br/><br/>
        <input type="file" onChange={e=>setFile(e.target.files[0])} /><br/><br/>
        <button type="submit">Upload Brain Session</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
