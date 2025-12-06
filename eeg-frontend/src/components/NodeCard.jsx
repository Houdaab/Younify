import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

const colors = ["#D0E6A5", "#FFDD94", "#FA897B", "#A28BD4", "#86E3CE"];

export default function NodeCard({ node, index }) {
  return (
    <Card sx={{ background: colors[index % colors.length], borderRadius: 2, padding: 1 }}>
      <CardContent>
        <Typography variant="subtitle1">Node {index + 1}</Typography>
        <Typography variant="body2"><strong>Hash:</strong> {node.hash}</Typography>
        <Typography variant="body2"><strong>Prev:</strong> {node.previous_hash || "None"}</Typography>
        <Typography variant="body2">
          <strong>Data:</strong> {JSON.stringify(node.state_data).slice(0, 50)}...
        </Typography>
      </CardContent>
    </Card>
  );
}
