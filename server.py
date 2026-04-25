#!/usr/bin/env python3
"""Voice Notes server: SPA routing + API + static files."""

import os
import re
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
APP_HTML = os.path.join(BASE_DIR, "voice-notes.html")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

session_folders = {}


def slugify(text):
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text[:60] or 'untitled'


def get_session_dir(session_id, title=None):
    if session_id in session_folders:
        return session_folders[session_id]

    date_str = datetime.now().strftime("%Y-%m-%d")
    name = slugify(title) if title else session_id
    folder_name = f"{date_str}_{name}"
    folder_path = os.path.join(RECORDINGS_DIR, folder_name)

    if os.path.exists(folder_path):
        i = 2
        while os.path.exists(f"{folder_path}-{i}"):
            i += 1
        folder_path = f"{folder_path}-{i}"

    os.makedirs(folder_path, exist_ok=True)
    session_folders[session_id] = folder_path
    return folder_path


class Handler(SimpleHTTPRequestHandler):

    def do_GET(self):
        # ── API routes ──
        if self.path == "/api/recordings":
            sessions = []
            for folder in sorted(os.listdir(RECORDINGS_DIR), reverse=True):
                folder_path = os.path.join(RECORDINGS_DIR, folder)
                if not os.path.isdir(folder_path):
                    continue
                notes_path = os.path.join(folder_path, "notes.json")
                has_audio = os.path.exists(os.path.join(folder_path, "audio.webm"))
                title = folder
                session_id = None
                created_at = None
                if os.path.exists(notes_path):
                    try:
                        with open(notes_path) as f:
                            data = json.load(f)
                        title = data.get("title", folder)
                        session_id = data.get("sessionId")
                        created_at = data.get("createdAt")
                    except Exception:
                        pass
                # Fallback to folder mtime if no createdAt
                if not created_at:
                    created_at = int(os.path.getmtime(folder_path) * 1000)
                sessions.append({
                    "folder": folder,
                    "title": title or folder,
                    "hasAudio": has_audio,
                    "sessionId": session_id,
                    "createdAt": created_at,
                })
            sessions.sort(key=lambda s: s.get("createdAt", 0), reverse=True)
            self._respond(200, sessions)
            return

        if self.path.startswith("/api/recording/"):
            folder = self.path.split("/api/recording/", 1)[1]
            folder_path = os.path.join(RECORDINGS_DIR, folder)
            notes_path = os.path.join(folder_path, "notes.json")
            if os.path.exists(notes_path):
                with open(notes_path) as f:
                    data = json.load(f)
                data["hasAudio"] = os.path.exists(os.path.join(folder_path, "audio.webm"))
                data["audioUrl"] = f"/recordings/{folder}/audio.webm" if data["hasAudio"] else None
                self._respond(200, data)
            else:
                self._respond(404, {"error": "not found"})
            return

        # ── Static files (recordings audio, onboarding assets, favicons, etc.) ──
        if (self.path.startswith("/recordings/")
                or self.path.startswith("/onboarding/")
                or self.path in ("/favicon.svg", "/favicon.png", "/favicon.ico", "/apple-touch-icon.png")):
            super().do_GET()
            return

        # ── SPA: serve app HTML for all other routes ──
        # This handles /, /recording/xxx, etc.
        self._serve_app()

    def do_POST(self):
        if self.path == "/api/save-audio":
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
            session = self.headers.get("X-Session-Id", datetime.now().strftime("%Y%m%d_%H%M%S"))
            title = self.headers.get("X-Title", None)
            folder = get_session_dir(session, title)
            filepath = os.path.join(folder, "audio.webm")
            with open(filepath, "wb") as f:
                f.write(data)
            self._respond(200, {"saved": filepath})

        elif self.path == "/api/save-notes":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            session = data.get("sessionId", datetime.now().strftime("%Y%m%d_%H%M%S"))
            title = data.get("title", None)

            # Overwrite: use existing folder directly
            explicit_folder = data.pop("folder", None)
            if explicit_folder:
                folder = os.path.join(RECORDINGS_DIR, explicit_folder)
            else:
                folder = get_session_dir(session, title)

            # Save-as-new with linked audio: symlink audio from source session
            linked_audio = data.pop("linkedAudio", None)
            if linked_audio:
                src_audio = os.path.join(RECORDINGS_DIR, linked_audio, "audio.webm")
                dst_audio = os.path.join(folder, "audio.webm")
                if os.path.exists(src_audio) and not os.path.exists(dst_audio):
                    os.makedirs(folder, exist_ok=True)
                    os.symlink(os.path.abspath(src_audio), dst_audio)

            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, "notes.json")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self._respond(200, {"saved": filepath, "folder": os.path.basename(folder)})

        elif self.path.startswith("/api/delete/"):
            folder = self.path.split("/api/delete/", 1)[1]
            folder_path = os.path.join(RECORDINGS_DIR, folder)
            if os.path.isdir(folder_path):
                import shutil
                shutil.rmtree(folder_path)
                self._respond(200, {"deleted": folder})
            else:
                self._respond(404, {"error": "not found"})

        else:
            self._respond(404, {"error": "not found"})

    def _serve_app(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        with open(APP_HTML, "rb") as f:
            self.wfile.write(f.read())

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Session-Id, X-Title")
        self.end_headers()


if __name__ == "__main__":
    port = 8091
    print(f"Serving on http://localhost:{port}")
    print(f"Recordings saved to {RECORDINGS_DIR}")
    HTTPServer(("", port), Handler).serve_forever()
