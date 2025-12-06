const BASE_URL = "http://localhost:8000";

export async function listChains() {
  const res = await fetch(`${BASE_URL}/chains`);
  return res.json();
}

export async function createChain(data) {
  const res = await fetch(`${BASE_URL}/chains/new`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function addNode(chain_id, file) {
  const formData = new FormData();
  formData.append("state_data", file);

  const res = await fetch(`${BASE_URL}/chain/${chain_id}/add_node`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function listVideos() {
  const res = await fetch(`${BASE_URL}/videos`);
  return res.json();
}

export async function uploadVideo(user_id, file) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", user_id);

  const res = await fetch(`${BASE_URL}/upload?user_id=${user_id}`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function getChain(chain_id) {
  const res = await fetch(`${BASE_URL}/chain/${chain_id}`);
  return res.json();
}
