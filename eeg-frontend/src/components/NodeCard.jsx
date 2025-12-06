import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

export default function NodeCard({ node, index }) {
  return (
    <Card sx={{ padding: 1 }}>
      <CardContent>
        <Typography variant="subtitle1">Node {index + 1}</Typography>
        <Typography variant="body2">Hash: {node.hash}</Typography>
        <Typography variant="body2">Prev: {node.previous_hash}</Typography>
        <Typography variant="body2">
          Data: {JSON.stringify(node.state_data).slice(0, 50)}...
        </Typography>
      </CardContent>
    </Card>
  );
}
