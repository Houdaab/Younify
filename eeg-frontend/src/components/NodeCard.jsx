
import { Card, CardContent, Typography, Box } from "@mui/material";

export default function NodeCard({ node }) {
  return (
    <Card
      sx={{
        width: 200,
        margin: 2,
        borderRadius: 3,
        boxShadow: 6,
        background: "#e1f5fe",
        transition: "transform 0.3s",
        "&:hover": { transform: "scale(1.05)" }
      }}
    >
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          Previous Hash:
        </Typography>
        <Box
          sx={{
            wordBreak: "break-all",
            fontSize: "0.75rem",
            background: "#b3e5fc",
            padding: "4px 6px",
            borderRadius: 1,
            marginBottom: 1
          }}
        >
          {node.previous_hash}
        </Box>
        <Typography variant="body2" color="text.secondary">
          Current Hash:
        </Typography>
        <Box
          sx={{
            wordBreak: "break-all",
            fontSize: "0.75rem",
            background: "#81d4fa",
            padding: "4px 6px",
            borderRadius: 1
          }}
        >
          {node.hash}
        </Box>
      </CardContent>
    </Card>
  );
}
