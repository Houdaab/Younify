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

  useEffect(() => { listChains().then(setUsers); }, []);
  useEffect(() => { fetchVideos(); }, []);

  useEffect(() => {
    if (selectedUser) {
      getChain(selectedUser._id).then(data => setNodes(data.nodes || []));
    } else setNodes([]);
  }, [selectedUser]);

  const fetchVideos = () => {
    listVideos().then(d => setVideos(d.videos));
  };

  const handleVideoUpload = async () => {
    if (!selectedUser || !videoFile) return;
    setLoading(true);
    await uploadVideo(selectedUser._id, videoFile);
    setVideoFile(null);
    fetchVideos();
    setLoading(false);
  };

  const handleEEGUpload = async () => {
    if (!selectedUser || !eegFile) return;
    setLoading(true);
    await uploadEEG(selectedUser._id, eegFile);
    setEegFile(null);
    fetchVideos();
    setLoading(false);
  };

  return (
    <Container sx={{ paddingY: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>EEG Dashboard</Typography>
      <Box sx={{ marginY: 2 }}>
        <UserSelect users={users} value={selectedUser} onChange={setSelectedUser} />
      </Box>

      {nav === "home" && <Typography align="center">Select a user to see content</Typography>}

      {nav === "videos" && (
        <Grid container spacing={2}>
          {videos.map(v => <Grid item key={v.video_id}><VideoCard video={v} /></Grid>)}
        </Grid>
      )}

      {nav === "upload" && selectedUser && (
        <Box>
          <Box sx={{ marginY: 2 }}>
            <input type="file" accept="video/*" onChange={e => setVideoFile(e.target.files[0])} />
            <Button variant="contained" onClick={handleVideoUpload} disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Upload Video"}
            </Button>
          </Box>
          <Box sx={{ marginY: 2 }}>
            <input type="file" accept=".csv" onChange={e => setEegFile(e.target.files[0])} />
            <Button variant="contained" onClick={handleEEGUpload} disabled={loading}>
              {loading ? <CircularProgress size={24} /> : "Upload EEG"}
            </Button>
          </Box>
        </Box>
      )}

      {nav === "blockchain" && selectedUser && (
        <Grid container spacing={2}>
          {nodes.map((n,i) => <Grid item key={i}><NodeCard node={n} index={i} /></Grid>)}
        </Grid>
      )}

      <Paper sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}>
        <BottomNavigation value={nav} onChange={(e, v)=>setNav(v)}>
          <BottomNavigationAction label="Home" value="home" icon={<Home />} />
          <BottomNavigationAction label="Videos" value="videos" icon={<VideoLibrary />} />
          <BottomNavigationAction label="Upload" value="upload" icon={<UploadFile />} />
          <BottomNavigationAction label="Blockchain" value="blockchain" icon={<AccountTree />} />
        </BottomNavigation>
      </Paper>
    </Container>
  );
}
