import { useEffect, useState } from "react";
import {
  Container,
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Button,
  BottomNavigation,
  BottomNavigationAction,
  Paper,
} from "@mui/material";
import { VideoLibrary, UploadFile, AccountTree, Home } from "@mui/icons-material";

import UserSelect from "../components/UserSelect";
import NodeCard from "../components/NodeCard";
import VideoCard from "../components/VideoCard";

export default function MainPage() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [videos, setVideos] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [videoFile, setVideoFile] = useState(null);
  const [navValue, setNavValue] = useState("home");

  // Fetch users
  useEffect(() => {
    fetch("http://localhost:8000/chains")
      .then((res) => res.json())
      .then((data) => setUsers(data))
      .catch(console.error);
  }, []);

  // Fetch videos
  useEffect(() => {
    fetch("http://localhost:8000/videos")
      .then((res) => res.json())
      .then((data) => setVideos(data.videos))
      .catch(console.error);
  }, []);

  // Fetch blockchain nodes when user changes
  useEffect(() => {
    if (!selectedUser) return;
    fetch(`http://localhost:8000/chain/${selectedUser}`)
      .then((res) => res.json())
      .then((data) => setNodes(data.nodes || []))
      .catch(console.error);
  }, [selectedUser]);

  // Upload video
  const handleVideoUpload = async () => {
    if (!videoFile || !selectedUser) return;

    const formData = new FormData();
    formData.append("file", videoFile);
    formData.append("user_id", selectedUser);

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    console.log(data);

    // Refresh videos
    fetch("http://localhost:8000/videos")
      .then((res) => res.json())
      .then((data) => setVideos(data.videos))
      .catch(console.error);

    setVideoFile(null);
  };

  return (
    <Container sx={{ paddingY: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        EEG Blockchain & Video Dashboard
      </Typography>

      {/* User selection */}
      <Box sx={{ marginY: 2 }}>
        <UserSelect
          value={selectedUser}
          onChange={setSelectedUser}
          users={users.map((u) => ({
            id: u._id,
            first_name: u.first_name,
            last_name: u.last_name,
          }))}
        />
      </Box>

      {/* Blockchain nodes */}
      {selectedUser && (
        <Box sx={{ marginY: 4 }}>
          <Typography variant="h5" gutterBottom>
            Blockchain Nodes for User
          </Typography>
          <Grid container spacing={2}>
            {nodes.map((node, idx) => (
              <Grid item key={idx}>
                <NodeCard node={node} />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Video upload */}
      {selectedUser && (
        <Box sx={{ marginY: 4 }}>
          <Typography variant="h5" gutterBottom>
            Upload Video
          </Typography>
          <input
            type="file"
            accept="video/*"
            onChange={(e) => setVideoFile(e.target.files[0])}
          />
          <Button
            variant="contained"
            color="primary"
            sx={{ marginLeft: 2 }}
            onClick={handleVideoUpload}
          >
            Upload
          </Button>
        </Box>
      )}

      {/* Videos */}
      <Box sx={{ marginY: 4 }}>
        <Typography variant="h5" gutterBottom>
          Videos
        </Typography>
        <Grid container spacing={2}>
          {videos.map((v) => (
            <Grid item key={v.video_id}>
              <VideoCard video={v} />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Bottom navigation */}
      <Paper
        sx={{ position: "fixed", bottom: 0, left: 0, right: 0 }}
        elevation={3}
      >
        <BottomNavigation
          value={navValue}
          onChange={(e, newValue) => setNavValue(newValue)}
        >
          <BottomNavigationAction label="Home" value="home" icon={<Home />} />
          <BottomNavigationAction
            label="Videos"
            value="videos"
            icon={<VideoLibrary />}
          />
          <BottomNavigationAction
            label="Upload"
            value="upload"
            icon={<UploadFile />}
          />
          <BottomNavigationAction
            label="Blockchain"
            value="blockchain"
            icon={<AccountTree />}
          />
        </BottomNavigation>
      </Paper>
    </Container>
  );
}
