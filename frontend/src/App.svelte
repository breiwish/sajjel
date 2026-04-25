<script>
  import Recorder from "./lib/Recorder.svelte";
  import NoteEditor from "./lib/NoteEditor.svelte";
  import TagSidebar from "./lib/TagSidebar.svelte";
  import Player from "./lib/Player.svelte";
  import Transcript from "./lib/Transcript.svelte";
  import LectureList from "./lib/LectureList.svelte";
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
      if (res.transcript) {
        transcriptData = res.transcript;
      }
      if (res.status !== "transcribing") {
        clearInterval(pollInterval);
      }
    }, 3000);
  }

  function backToHome() {
    view = "home";
    if (pollInterval) clearInterval(pollInterval);
    if (lectureListRef) lectureListRef.refresh();
  }
</script>

<div class="app">
  <header>
    <div class="logo" onclick={backToHome}>
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
        <!-- open book facing up, pages spread left and right -->
        <path d="M16 24C16 24 10 22 4 23L6 10C10 9 15 10 16 12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M16 24C16 24 22 22 28 23L26 10C22 9 17 10 16 12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- spine -->
        <line x1="16" y1="12" x2="16" y2="24" stroke="currentColor" stroke-width="1"/>
        <!-- sound waves emanating upward -->
        <path d="M12 8C13.5 6 18.5 6 20 8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        <path d="M10 5C12.5 2 19.5 2 22 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" opacity="0.5"/>
      </svg>
      <span class="logo-text">Udhkur</span>
    </div>
    {#if view !== "recording"}
      <button class="new-btn" onclick={startNew}>+ New Recording</button>
    {/if}
  </header>

  {#if view === "home"}
    <div class="home">
      <LectureList bind:this={lectureListRef} onselect={openLecture} />
    </div>

  {:else if view === "recording"}
    <div class="toolbar">
      <Recorder bind:this={recorder} onstarted={() => {}} onstopped={onRecordStopped} />
      {#if audioBlob}
        <button class="save-btn" onclick={save}>Save Lecture</button>
      {/if}
      <button class="back-btn" onclick={backToHome}>← Back</button>
    </div>
    <main>
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
      {#if transcriptStatus !== "transcribing"}
        <button class="transcribe-btn" onclick={transcribe}>
          {transcriptData ? "Re-transcribe" : "Transcribe"}
        </button>
      {/if}
      <button class="back-btn" onclick={backToHome}>← Back</button>
    </div>
    <main>
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
  .app { display: flex; flex-direction: column; height: 100vh; }

  header {
    padding: 14px 20px; border-bottom: 1px solid #222;
    display: flex; align-items: center; gap: 12px;
  }
  .logo {
    display: flex; align-items: center; gap: 10px; flex: 1;
    cursor: pointer; color: #fff;
  }
  .logo:hover { opacity: 0.85; }
  .logo-text { font-size: 20px; font-weight: 600; letter-spacing: 0.5px; }

  .toolbar {
    padding: 10px 20px; border-bottom: 1px solid #1e1e1e;
    display: flex; align-items: center; gap: 10px;
  }
  .lecture-title { font-size: 15px; color: #ddd; flex: 1; font-weight: 500; }

  main { display: flex; flex: 1; overflow: hidden; }
  .note-pane { flex: 1; display: flex; flex-direction: column; }
  .home { flex: 1; overflow-y: auto; }

  button {
    border: none; cursor: pointer; border-radius: 6px; font-size: 13px;
    padding: 7px 14px; transition: background 0.15s;
  }
  .new-btn { background: #44aaff; color: #fff; }
  .new-btn:hover { background: #2299ee; }
  .save-btn { background: #1a2a1a; color: #6c6; border: 1px solid #2a3a2a; }
  .save-btn:hover { background: #223322; }
  .transcribe-btn { background: #2a1a2a; color: #c6c; border: 1px solid #3a2a3a; }
  .transcribe-btn:hover { background: #332233; }
  .back-btn { background: #2a2a2a; color: #888; }
  .back-btn:hover { background: #333; }
</style>
