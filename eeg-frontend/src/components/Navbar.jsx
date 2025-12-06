import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: "1rem", background: "#0d1b2a", color: "#fff" }}>
      <Link to="/" style={{ marginRight: 15, color: "#fff" }}>Videos</Link>
      <Link to="/add-user" style={{ marginRight: 15, color: "#fff" }}>Add User</Link>
      <Link to="/add-node" style={{ marginRight: 15, color: "#fff" }}>Add Node</Link>
      <Link to="/upload-video" style={{ marginRight: 15, color: "#fff" }}>Upload Video</Link>
      <Link to="/blockchain" style={{ color: "#fff" }}>Blockchain</Link>
    </nav>
  );
}
