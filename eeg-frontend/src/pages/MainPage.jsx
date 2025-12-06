import React, { useEffect, useState } from "react";
import { Container, Typography, Box, Grid, Paper, Button, CircularProgress } from "@mui/material";
import { BottomNavigation, BottomNavigationAction } from "@mui/material";
import { VideoLibrary, UploadFile, Home, AccountTree } from "@mui/icons-material";
import VideoCard from "../components/VideoCard";
import NodeCard from "../components/NodeCard";
import UserSelect from "../components/UserSelect";
import { listChains, listVideos, uploadVideo, uploadEEG, getChain } from "../api";

export default function MainPage() {
  const [nav, setNav] = useState("home");
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [videos, setVideos] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [videoFile, setVideoFile] = useState(null);
  const [eegFile, setEegFile] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch users on load
  useEffect(() => {
    listChains().then(res => {
      setUsers(Array.isArray(res) ? res : [res]); // handle single user response
      if (res && !Array.isArray(res)) setSelectedUser(res); // select first user automatically
    });
  }, []);

  // Fetch videos
  const fetchVideos = () => {
    listVideos().then(d => {
      if (d.videos) setVideos(d.videos.map(v => ({
        ...v,
        url: `${v.url.startsWith("http") ? "" : "http://localhost:8000"}${v.url}`
      })));
    });
  };

  useEffect(() => { fetchVideos(); }, []);

  // Fetch blockchain nodes when user changes
  useEffect(() => {
    if (selectedUser) {
      getChain(selectedUser._id).then(data => setNodes(data.nodes || []));
    } else setNodes([]);
  }, [selectedUser]);

  // Upload video
  const handleVideoUpload = async () => {
    if (!selectedUser || !videoFile) return;
    setLoading(true);
    await uploadVideo(selectedUser._id, videoFile);
    setVideoFile(null);
    fetchVideos();
    setLoading(false);
  };

  // Upload EEG / brain session
  const handleEEGUpload = async () => {
    if (!selectedUser || !eegFile) return;
    setLoading(true);
    await uploadEEG(selectedUser._id, eegFile);
    setEegFile(null);
    fetchVideos(); // refresh videos after EEG (if applicable)
    setLoading(false);
  };

  return (
    <Container sx={{ paddingY: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>EEG Dashboard</Typography>

      <Box sx={{ marginY: 2 }}>
        <UserSelect users={users} value={selectedUser} onChange={setSelectedUser} />
      </Box>

      {nav === "home" && selectedUser && (
        <Box sx={{ marginY: 2, padding: 2, border: "2px solid #0f4c75", borderRadius: 2, background: "#bbe1fa" }}>
          <Typography variant="h5">{selectedUser.first_name} {selectedUser.last_name}</Typography>
          <Typography variant="body1">Gender: {selectedUser.gender}</Typography>
          <Typography variant="body2">Nodes: {nodes.length}</Typography>
        </Box>
      )}

      {nav === "videos" && (
        <Grid container spacing={2}>
          {videos.length === 0 ? (
            <Typography>No videos uploaded yet.</Typography>
          ) : videos.map(v => (
            <Grid item key={v.video_id}>
              <VideoCard video={v} />
            </Grid>
          ))}
        </Grid>
      )}

      {nav === "upload" && selectedUser && (
        <Box>
          <Box sx={{ marginY: 2 }}>
            <Typography variant="h6">Upload Video</Typography>
            <input type="file" accept="video/*" onChange={e => setVideoFile(e.target.files[0])} />
            <Button variant="contained" onClick={handleVideoUpload} disabled={loading} sx={{ ml: 2 }}>
              {loading ? <CircularProgress size={24} /> : "Upload Video"}
            </Button>
          </Box>
          <Box sx={{ marginY: 2 }}>
            <Typography variant="h6">Upload EEG / Brain Session</Typography>
            <input type="file" accept=".csv" onChange={e => setEegFile(e.target.files[0])} />
            <Button variant="contained" onClick={handleEEGUpload} disabled={loading} sx={{ ml: 2 }}>
              {loading ? <CircularProgress size={24} /> : "Upload EEG"}
            </Button>
          </Box>
        </Box>
      )}

      {nav === "blockchain" && selectedUser && (
        <Grid container spacing={2}>
          {nodes.length === 0 ? (
            <Typography>No nodes yet.</Typography>
          ) : nodes.map((n, i) => (
            <Grid item key={i}>
              <NodeCard node={n} index={i} />
            </Grid>
          ))}
        </Grid>
      )}

      <Paper sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}>
        <BottomNavigation value={nav} onChange={(e, v) => setNav(v)}>
          <BottomNavigationAction label="Home" value="home" icon={<Home />} />
          <BottomNavigationAction label="Videos" value="videos" icon={<VideoLibrary />} />
          <BottomNavigationAction label="Upload" value="upload" icon={<UploadFile />} />
          <BottomNavigationAction label="Blockchain" value="blockchain" icon={<AccountTree />} />
        </BottomNavigation>
      </Paper>
    </Container>
  );
}
