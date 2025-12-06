const BASE = "http://localhost:8000";

export async function listChains() {
  const res = await fetch(`${BASE}/chains`);
  return res.json();
}

export async function getChain(chainId) {
  const res = await fetch(`${BASE}/chain/${chainId}`);
  return res.json();
}

export async function createChain(userData) {
  const res = await fetch(`${BASE}/chains/new`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });
  return res.json();
}

export async function addNode(chainId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/chain/${chainId}/add_node`, {
    method: "POST",
    body: form,
  });
  return res.json();
}

export async function listVideos() {
  const res = await fetch(`${BASE}/videos`);
  return res.json();
}

export async function uploadVideo(userId, file) {
  if (!userId || !file) throw new Error("User ID and file are required");

  const formData = new FormData();
  formData.append("file", file);

  // user_id must go as query param
  const url = new URL("http://localhost:8000/upload");
  url.searchParams.append("user_id", userId);

  const res = await fetch(url.toString(), {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: ${text}`);
  }

  return res.json();
}

export async function uploadEEG(userId, file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/supply_data/${userId}`, { method: "POST", body: form });
  return res.json();
}
