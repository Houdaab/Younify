import { FormControl, InputLabel, Select, MenuItem } from "@mui/material";
import { useState } from "react";

export default function UserSelect({ value, onChange }) {
  const [users] = useState([
    { _id: "1", first_name: "Alice", last_name: "Smith" },
    { _id: "2", first_name: "Bob", last_name: "Johnson" },
    { _id: "3", first_name: "Charlie", last_name: "Brown" }
  ]);

  return (
    <FormControl sx={{ minWidth: 200 }}>
      <InputLabel>Select User</InputLabel>
      <Select value={value} label="Select User" onChange={(e) => onChange(e.target.value)}>
        {users.map((u) => (
          <MenuItem key={u._id} value={u._id}>
            {u.first_name} {u.last_name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
