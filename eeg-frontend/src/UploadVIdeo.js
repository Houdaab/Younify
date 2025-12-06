import { useState, useEffect } from "react";
import { listChains, uploadVideo } from "../api";

export default function UploadVideo() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    listChains().then(setUsers).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedUser || !file) {
      setMessage("Please select a user and a video file.");
      return;
    }

    try {
      const res = await uploadVideo(selectedUser, file);
      setMessage(`Video uploaded successfully: ${res.video_id}`);
      setFile(null);
    } catch (err) {
      console.error(err);
      setMessage("Upload failed. Make sure the file type is supported (.mp4, .mov, .avi, .mkv, .webm).");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Upload Video for User</h2>
      <form onSubmit={handleSubmit}>
        <select
          value={selectedUser}
          onChange={(e) => setSelectedUser(e.target.value)}
        >
          <option value="">Select user</option>
          {users.map((u) => (
            <option key={u._id} value={u._id}>
              {u.first_name} {u.last_name}
            </option>
          ))}
        </select>
        <br /><br />
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <br /><br />
        <button type="submit">Upload Video</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
