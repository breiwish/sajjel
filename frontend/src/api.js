const BASE = "http://localhost:8000";

export async function createLecture(audio, { title, notes, tags, duration }) {
  const form = new FormData();
  form.append("audio", audio);
  form.append("title", title || "Untitled Lecture");
  form.append("notes", notes || "");
  form.append("tags_json", JSON.stringify(tags || []));
  form.append("duration", duration || 0);
  const res = await fetch(`${BASE}/api/lectures`, { method: "POST", body: form });
  return res.json();
}

export async function listLectures() {
  const res = await fetch(`${BASE}/api/lectures`);
  return res.json();
}

export async function getLecture(id) {
  const res = await fetch(`${BASE}/api/lectures/${id}`);
  return res.json();
}

export async function deleteLecture(id) {
  const res = await fetch(`${BASE}/api/lectures/${id}`, { method: "DELETE" });
  return res.json();
}

export async function startTranscription(id, diarize = false) {
  const res = await fetch(`${BASE}/api/lectures/${id}/transcribe?diarize=${diarize}`, { method: "POST" });
  return res.json();
}

export async function getTranscript(id) {
  const res = await fetch(`${BASE}/api/lectures/${id}/transcript`);
  return res.json();
}

export function audioUrl(filename) {
  return `${BASE}/api/audio/${filename}`;
}
