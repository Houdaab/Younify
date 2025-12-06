import { useState } from "react";
import { Container, Grid, Typography, Paper, Box, Button, BottomNavigation, BottomNavigationAction } from "@mui/material";
import { VideoLibrary, UploadFile, Home } from "@mui/icons-material";
import VideoCard from "../components/VideoCard";
import UserSelect from "../components/UserSelect";
import { videos as hardcodedVideos } from "../data/videos";

export default function MainPage() {
  const [selectedUser, setSelectedUser] = useState(null);
  const [file, setFile] = useState(null);
  const [videos, setVideos] = useState(hardcodedVideos);
  const [tab, setTab] = useState("videos");

  const handleUpload = (e) => {
    e.preventDefault();
    alert(`Uploading brain session for user: ${selectedUser}`);
    setFile(null);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#fefefe", paddingBottom: "80px" }}>
      <Container maxWidth="lg" sx={{ paddingTop: 4 }}>
        <Typography variant="h3" align="center" sx={{ color: "#1976d2", fontWeight: "bold", marginBottom: 4 }}>
          EEG Dashboard
        </Typography>

        {tab === "upload" && (
          <Paper sx={{ padding: 3, marginBottom: 4, boxShadow: 6, borderRadius: 3, backgroundColor: "#e3f2fd" }}>
            <Typography variant="h5" gutterBottom sx={{ color: "#0d47a1" }}>
              Upload Brain Session (Node)
            </Typography>
            <Box
              component="form"
              onSubmit={handleUpload}
              sx={{ display: "flex", gap: 2, alignItems: "center", flexWrap: "wrap" }}
            >
              <UserSelect value={selectedUser} onChange={setSelectedUser} />
              <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
              <Button variant="contained" color="primary" type="submit">
                Upload
              </Button>
            </Box>
          </Paper>
        )}

        {tab === "videos" && (
          <>
            <Typography variant="h5" gutterBottom sx={{ color: "#1976d2", marginBottom: 2 }}>
              Video Gallery
            </Typography>
            <Grid container spacing={3}>
              {videos.map((v) => (
                <Grid item key={v.video_id} xs={12} sm={6} md={4} lg={3}>
                  <VideoCard video={v} />
                </Grid>
              ))}
            </Grid>
          </>
        )}
      </Container>

      {/* Bottom Navigation */}
      <BottomNavigation
        sx={{
          width: "100%",
          position: "fixed",
          bottom: 0,
          backgroundColor: "#1976d2",
          color: "#fff",
          boxShadow: "0 -3px 10px rgba(0,0,0,0.2)"
        }}
        value={tab}
        onChange={(event, newValue) => setTab(newValue)}
      >
        <BottomNavigationAction label="Home" value="home" icon={<Home sx={{ color: "#fff" }} />} />
        <BottomNavigationAction label="Upload Node" value="upload" icon={<UploadFile sx={{ color: "#fff" }} />} />
        <BottomNavigationAction label="Videos" value="videos" icon={<VideoLibrary sx={{ color: "#fff" }} />} />
      </BottomNavigation>
    </div>
  );
}
