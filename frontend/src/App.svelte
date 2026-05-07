<script>
  import { onMount } from "svelte";
  import Recorder from "./lib/Recorder.svelte";
  import NoteEditor from "./lib/NoteEditor.svelte";
  import TagSidebar from "./lib/TagSidebar.svelte";
  import Player from "./lib/Player.svelte";
  import Transcript from "./lib/Transcript.svelte";
  import LectureList from "./lib/LectureList.svelte";
  import IconButton from "./lib/IconButton.svelte";
  import Icon from "./lib/Icon.svelte";
  import { createLecture, getLecture, startTranscription, getTranscript, audioUrl } from "./api.js";

  let view = $state("home");
  let notes = $state("");
  let tags = $state([]);
  let audioBlob = $state(null);
  let audioDuration = $state(0);
  let currentTime = $state(0);
  let recorder = $state(null);
  let player = $state(null);
  let lectureListRef = $state(null);

  let lecture = $state(null);
  let audioSrc = $state(null);
  let transcriptData = $state(null);
  let transcriptStatus = $state("recorded");
  let pollInterval = null;

  // Theme — light by default, persists in localStorage
  let theme = $state("light");
  onMount(() => {
    const saved = localStorage.getItem("sajjel-theme");
    if (saved === "dark" || saved === "light") theme = saved;
    applyTheme();
  });
  function applyTheme() {
    document.documentElement.dataset.theme = theme;
    if (theme === "dark") document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }
  function toggleTheme() {
    theme = theme === "light" ? "dark" : "light";
    localStorage.setItem("sajjel-theme", theme);
    applyTheme();
  }

  function startNew() {
    view = "recording";
    notes = "";
    tags = [];
    audioBlob = null;
    audioDuration = 0;
    lecture = null;
    audioSrc = null;
    transcriptData = null;
    transcriptStatus = "recorded";
  }

  function onRecordStopped(detail) {
    audioBlob = detail.blob;
    audioDuration = detail.duration;
    audioSrc = URL.createObjectURL(detail.blob);
  }

  function onNewTag(detail) {
    tags = [...tags, detail].sort((a, b) => a.time - b.time);
  }

  function onTagJump(tag) {
    if (player) player.seekTo(tag.time);
  }

  function onTranscriptSeek(detail) {
    if (player) player.seekTo(detail.time);
  }

  function onTimeUpdate(detail) {
    currentTime = detail.currentTime;
  }

  async function save() {
    if (!audioBlob) return;
    const title = prompt("Lecture title:", "Untitled Lecture");
    if (title === null) return;
    const result = await createLecture(audioBlob, { title, notes, tags, duration: audioDuration });
    lecture = result;
    audioSrc = audioUrl(result.audio_path);
    view = "lecture";
    if (lectureListRef) lectureListRef.refresh();
  }

  async function openLecture(lec) {
    const full = await getLecture(lec.id);
    lecture = full;
    notes = full.notes || "";
    tags = full.tags || [];
    audioSrc = full.audio_path ? audioUrl(full.audio_path) : null;
    transcriptData = full.transcript;
    transcriptStatus = full.status;
    view = "lecture";
  }

  async function transcribe() {
    if (!lecture) return;
    transcriptStatus = "transcribing";
    await startTranscription(lecture.id);
    pollInterval = setInterval(async () => {
      const res = await getTranscript(lecture.id);
      transcriptStatus = res.status;
      if (res.transcript) transcriptData = res.transcript;
      if (res.status !== "transcribing") clearInterval(pollInterval);
    }, 3000);
  }

  function backToHome() {
    view = "home";
    if (pollInterval) clearInterval(pollInterval);
  }
</script>

<div class="app">
  <header class="topbar">
    <button class="brand" onclick={backToHome} aria-label="Sajjel home">
      <span class="brand-mark">
        <!-- Minimal mark: stacked sound waves through a baseline -->
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 12h18"/>
          <path d="M7 8v8"/>
          <path d="M11 5v14"/>
          <path d="M15 8v8"/>
          <path d="M19 10v4"/>
        </svg>
      </span>
      <span class="brand-wordmark">
        <span class="brand-latin">Sajjel</span>
        <span class="brand-ar" lang="ar" dir="rtl">سَجِّلْ</span>
      </span>
    </button>

    <div class="topbar-actions">
      {#if view !== "recording"}
        <button class="btn btn-primary" onclick={startNew}>
          <Icon name="plus" size={16} />
          <span>New recording</span>
        </button>
      {/if}
      <IconButton label="Toggle theme" onclick={toggleTheme}>
        <Icon name={theme === "light" ? "moon" : "sun"} size={16} />
      </IconButton>
    </div>
  </header>

  {#if view === "home"}
    <div class="home">
      <LectureList bind:this={lectureListRef} onselect={openLecture} />
    </div>

  {:else if view === "recording"}
    <div class="toolbar">
      <Recorder bind:this={recorder} onstarted={() => {}} onstopped={onRecordStopped} />
      <div class="toolbar-spacer"></div>
      {#if audioBlob}
        <button class="btn btn-primary" onclick={save}>
          <Icon name="save" size={16} />
          <span>Save lecture</span>
        </button>
      {/if}
      <button class="btn btn-ghost" onclick={backToHome}>
        <Icon name="arrow-left" size={16} />
        <span>Back</span>
      </button>
    </div>
    <main class="workspace">
      <div class="note-pane">
        <NoteEditor
          bind:value={notes}
          getTimestamp={() => recorder?.getElapsedSeconds() || 0}
          onnewtag={onNewTag}
        />
      </div>
      <TagSidebar {tags} {currentTime} onjump={onTagJump} />
    </main>
    <Player bind:this={player} src={audioSrc} fallbackDuration={audioDuration} ontimeupdate={onTimeUpdate} />

  {:else if view === "lecture"}
    <div class="toolbar">
      <h2 class="lecture-title">{lecture?.title || "Lecture"}</h2>
      <div class="toolbar-spacer"></div>
      {#if transcriptStatus !== "transcribing"}
        <button class="btn btn-secondary" onclick={transcribe}>
          <Icon name="sparkles" size={16} />
          <span>{transcriptData ? "Re-transcribe" : "Transcribe"}</span>
        </button>
      {/if}
      <button class="btn btn-ghost" onclick={backToHome}>
        <Icon name="arrow-left" size={16} />
        <span>Back</span>
      </button>
    </div>
    <main class="workspace">
      <div class="note-pane">
        <NoteEditor bind:value={notes} disabled />
        <Transcript
          transcript={transcriptData}
          status={transcriptStatus}
          {currentTime}
          onseek={onTranscriptSeek}
        />
      </div>
      <TagSidebar {tags} {currentTime} onjump={onTagJump} />
    </main>
    <Player bind:this={player} src={audioSrc} fallbackDuration={audioDuration} ontimeupdate={onTimeUpdate} />
  {/if}
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--background);
    color: var(--foreground);
  }

  /* ── Topbar ────────────────────────────────────────────────────── */
  .topbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    border-bottom: 1px solid var(--border);
    background: var(--background);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    color: var(--foreground);
    border-radius: var(--radius-md);
    padding: 4px 6px;
    margin-left: -6px;
    transition: background 150ms ease-out;
  }
  .brand:hover { background: var(--accent); }

  .brand-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-md);
    background: var(--primary);
    color: var(--primary-foreground);
  }

  .brand-wordmark {
    display: flex;
    align-items: baseline;
    gap: 10px;
    line-height: 1;
  }
  .brand-latin {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.01em;
  }
  .brand-ar {
    font-family: "Aref Ruqaa", serif;
    font-size: 22px;
    color: var(--muted-foreground);
    font-weight: 400;
    line-height: 1;
  }

  .topbar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ── Toolbar (under topbar) ───────────────────────────────────── */
  .toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    border-bottom: 1px solid var(--border);
    background: var(--card);
  }
  .toolbar-spacer { flex: 1; }
  .lecture-title {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--foreground);
    letter-spacing: -0.01em;
    margin: 0;
  }

  /* ── Workspace ─────────────────────────────────────────────────── */
  .workspace {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  .note-pane {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .home { flex: 1; overflow-y: auto; }

  /* ── Buttons (shadcn parity) ──────────────────────────────────── */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    height: 32px;
    padding: 0 12px;
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: 500;
    line-height: 1;
    border: 1px solid transparent;
    transition: background 150ms ease-out, color 150ms ease-out, border-color 150ms ease-out;
    white-space: nowrap;
  }
  .btn-primary {
    background: var(--primary);
    color: var(--primary-foreground);
    box-shadow: var(--shadow-xs);
  }
  .btn-primary:hover { background: color-mix(in oklch, var(--primary) 90%, black); }
  .btn-secondary {
    background: var(--secondary);
    color: var(--secondary-foreground);
    border-color: var(--border);
    box-shadow: var(--shadow-xs);
  }
  .btn-secondary:hover { background: var(--accent); }
  .btn-ghost {
    background: transparent;
    color: var(--muted-foreground);
  }
  .btn-ghost:hover { background: var(--accent); color: var(--accent-foreground); }
</style>
