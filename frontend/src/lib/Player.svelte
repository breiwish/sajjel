<script>
  import { onDestroy } from "svelte";

  let { src = null, fallbackDuration = 0, ontimeupdate } = $props();

  let audio = $state(null);
  let isPlaying = $state(false);
  let currentTime = $state(0);
  let duration = $state(0);
  let interval;

  function fmtTime(s) {
    if (!s || !isFinite(s)) return "0:00";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  // Use actual duration if available, otherwise fallback from recorder
  function displayDuration() {
    if (duration && isFinite(duration) && duration > 0) return duration;
    return fallbackDuration || 0;
  }

  function toggle() {
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
      isPlaying = false;
      clearInterval(interval);
    } else {
      audio.play();
      isPlaying = true;
      interval = setInterval(() => {
        currentTime = audio.currentTime;
        // WebM often only reports duration after playback starts
        if (audio.duration && isFinite(audio.duration)) {
          duration = audio.duration;
        }
        ontimeupdate?.({ currentTime });
      }, 200);
    }
  }

  function seek(e) {
    if (!audio) return;
    audio.currentTime = parseFloat(e.target.value);
    currentTime = audio.currentTime;
    ontimeupdate?.({ currentTime });
  }

  function onLoaded() {
    if (audio.duration && isFinite(audio.duration)) {
      duration = audio.duration;
    }
  }

  function onEnded() {
    isPlaying = false;
    clearInterval(interval);
  }

  export function seekTo(time) {
    if (!audio) return;
    audio.currentTime = time;
    currentTime = time;
    if (!isPlaying) toggle();
  }

  onDestroy(() => clearInterval(interval));
</script>

{#if src}
  <audio bind:this={audio} {src} onloadedmetadata={onLoaded} onended={onEnded}></audio>
  <div class="player">
    <button class="play-btn" onclick={toggle}>
      {isPlaying ? "⏸ Pause" : "▶ Play"}
    </button>
    <input type="range" class="seek-bar" min="0" max={displayDuration() || 100} value={currentTime} step="0.1" oninput={seek}>
    <span class="timer">{fmtTime(currentTime)} / {fmtTime(displayDuration())}</span>
  </div>
{/if}

<style>
  .player {
    padding: 10px 16px; background: #111; border-top: 1px solid #1e1e1e;
    display: flex; align-items: center; gap: 10px;
  }
  .play-btn {
    border: none; cursor: pointer; border-radius: 6px; font-size: 13px;
    padding: 7px 14px; background: #2a2a2a; color: #ccc;
  }
  .play-btn:hover { background: #333; }
  .seek-bar { flex: 1; accent-color: #44aaff; height: 3px; cursor: pointer; }
  .timer { font-size: 13px; font-family: monospace; color: #888; min-width: 100px; text-align: right; }
</style>
