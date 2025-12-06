import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

export default function VideoCard({ video }) {
  return (
    <Card sx={{ maxWidth: 300 }}>
      <video width="100%" controls src={video.url} />
      <CardContent>
        <Typography>{video.author.first_name} {video.author.last_name}</Typography>
        <Typography color={video.is_human ? "green" : "red"}>
          {video.is_human ? "REAL" : "FAKE"}
        </Typography>
      </CardContent>
    </Card>
  );
}
