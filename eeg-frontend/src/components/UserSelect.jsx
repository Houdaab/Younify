import { FormControl, InputLabel, Select, MenuItem } from "@mui/material";

export default function UserSelect({ value, onChange, users }) {
  return (
    <FormControl sx={{ minWidth: 200 }}>
      <InputLabel id="user-select-label">Select User</InputLabel>
      <Select
        labelId="user-select-label"
        value={value || ""}
        label="Select User"
        onChange={(e) => onChange(e.target.value)}
      >
        {users.map((u) => (
          <MenuItem key={u.id} value={u.id}>
            {u.first_name} {u.last_name}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
