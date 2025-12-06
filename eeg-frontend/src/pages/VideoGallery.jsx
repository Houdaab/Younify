import { useEffect, useState } from "react";
import { listVideos } from "../api";

export default function VideoGallery() {
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    listVideos().then(data => setVideos(data.videos));
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>All Videos</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, 250px)", gap: 20 }}>
        {videos.map(v => (
          <div key={v.video_id} style={{ border: "1px solid #ccc", padding: 10, borderRadius: 8 }}>
            <video src={v.url} controls width="250" />
            <p>{v.author.first_name} {v.author.last_name}</p>
            <p style={{ color: v.is_human ? "green" : "red" }}>
              {v.is_human ? "REAL" : "FAKE"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
