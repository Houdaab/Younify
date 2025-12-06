import React from "react";
import { FormControl, InputLabel, Select, MenuItem } from "@mui/material";

export default function UserSelect({ users, value, onChange }) {
  return (
    <FormControl fullWidth>
      <InputLabel>User</InputLabel>
      <Select value={value?._id || ""} label="User" onChange={e => {
        const selected = users.find(u => u._id === e.target.value);
        onChange(selected);
      }}>
        {users.map(u => (
          <MenuItem key={u._id} value={u._id}>
            {u.first_name} {u.last_name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
