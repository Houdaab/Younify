import { useState } from "react";
import { createChain } from "../api";

export default function AddUser() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [gender, setGender] = useState("male");
  const [message, setMessage] = useState("");

  const handleSubmit = async e => {
    e.preventDefault();
    const res = await createChain({ first_name: firstName, last_name: lastName, gender });
    setMessage(`User created: ${res._id}`);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Add New User</h2>
      <form onSubmit={handleSubmit}>
        <input placeholder="First Name" value={firstName} onChange={e=>setFirstName(e.target.value)} /><br/><br/>
        <input placeholder="Last Name" value={lastName} onChange={e=>setLastName(e.target.value)} /><br/><br/>
        <select value={gender} onChange={e=>setGender(e.target.value)}>
          <option value="male">Male</option>
          <option value="female">Female</option>
        </select><br/><br/>
        <button type="submit">Add User</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
