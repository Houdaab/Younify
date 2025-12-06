import { useState, useEffect } from "react";
import { listChains, uploadVideo } from "../api";
import { useNavigate } from "react-router-dom";

export default function UploadVideo() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    listChains().then(setUsers);
  }, []);

  const handleSubmit = async e => {
    e.preventDefault();
    if (!selectedUser || !file) return;
    await uploadVideo(selectedUser, file);
    navigate("/");
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Upload Video for User</h2>
      <form onSubmit={handleSubmit}>
        <select value={selectedUser} onChange={e=>setSelectedUser(e.target.value)}>
          <option value="">Select user</option>
          {users.map(u => <option key={u._id} value={u._id}>{u.first_name} {u.last_name}</option>)}
        </select><br/><br/>
        <input type="file" onChange={e=>setFile(e.target.files[0])} /><br/><br/>
        <button type="submit">Upload Video</button>
      </form>
    </div>
  );
}
