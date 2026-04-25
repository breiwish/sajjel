# Sajjel · سَجِّلْ

Synchronized voice + text note-taking. Record audio while typing notes; every keystroke is timestamped against the audio so you can scrub back to the exact moment any sentence was written.

> _Sajjil_ (Arabic: سَجِّلْ) — imperative: **record**.

## Features

- **Audio + notes in lockstep.** Delta snapshots every 50 ms reconstruct the text at any timestamp during playback.
- **`#Tag Name#` syntax.** Wrap a phrase in hashes and it becomes a timestamped tag in the side panel — click to jump to that moment.
- **Pin markers (Ctrl+M).** Drop an unnamed pin during recording, name it later.
- **Live Text replay.** During playback, watch the text rewind/replay alongside the audio.
- **Nudge controls.** Right-click any tag to fine-tune its timestamp (±0.1s / ±1s / ±5s).
- **Auto-save to disk.** Sessions persist as folders under `recordings/` (audio + notes JSON).
- **Session picker.** Load past sessions, sorted newest-first; delete with confirmation.
- **Onboarding.** First-run guide with screenshots and GIFs.

## Architecture

Single-file SPA + Python static server.

- `voice-notes.html` — the entire app (inline CSS + JS, no build step).
- `server.py` — Python `http.server` with SPA routing on port **8091**, plus a small JSON API for save/load/delete.
- `recordings/` — one folder per session: `audio.webm` + `notes.json`.
- `onboarding/` — screenshots and GIFs shown in the first-run guide.

### Storage

- **Audio** → `audio.webm` per session folder (MediaRecorder, opus codec).
- **Notes** → `notes.json` with `{title, text, tags[], snapshots[], createdAt}`. Snapshots are deltas: `{t, p, d, i}` (time, position, deleted count, inserted text). The first entry is a baseline `{t, text}`.

## Running

```sh
python3 server.py
# open http://localhost:8091
```

No dependencies for the core app. Onboarding screenshot regeneration uses Pillow + arabic-reshaper (optional).

## Keyboard

| Key                                                       | Action                                |
| --------------------------------------------------------- | ------------------------------------- |
| `⏺ Record` button or `Space` (when not focused in editor) | Start/stop recording                  |
| `Ctrl+M`                                                  | Drop pin marker at current audio time |
| `← / →`                                                   | Scrub audio (during playback)         |
| `#word#` in note text                                     | Create a tag at current audio time    |
| Right-click a tag                                         | Expand nudge controls                 |
| Click a tag                                               | Jump audio to tag time                |

## Files of interest

- `voice-notes.html` lines 200–230 — header
- `voice-notes.html` (search `computeDelta`) — delta snapshot capture
- `voice-notes.html` (search `reconstructAtTime`) — text replay during playback
- `server.py` — SPA routing + `/api/recordings`, `/api/save-notes`, `/api/save-audio`, `/api/delete/:folder`

## License

Personal project. No license granted.
