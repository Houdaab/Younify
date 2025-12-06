import { Card, CardContent, Typography, CardMedia, Chip } from "@mui/material";

export default function VideoCard({ video }) {
  const { url, author, is_human, filename } = video;
  const backendUrl = "http://localhost:8000";

  return (
    <Card
      sx={{
        maxWidth: 300,
        borderRadius: 3,
        boxShadow: 6,
        transition: "transform 0.3s",
        "&:hover": { transform: "scale(1.05)" },
        backgroundColor: "#e3f2fd"
      }}
    >
      <CardMedia
        component="video"
        src={`${backendUrl}${url}`}   // <-- fetch from FastAPI server
        controls
        sx={{ height: 180, borderRadius: "8px 8px 0 0" }}
      />
      <CardContent>
        <Typography variant="h6" sx={{ fontWeight: "bold" }}>
          {author?.first_name || "Unknown"} {author?.last_name || ""}
        </Typography>
        <Chip
          label={is_human ? "REAL" : "FAKE"}
          color={is_human ? "success" : "error"}
          sx={{ marginTop: 1, marginBottom: 1 }}
        />
        <Typography variant="body2" color="text.secondary">
          {filename}
        </Typography>
      </CardContent>
    </Card>
  );
}
