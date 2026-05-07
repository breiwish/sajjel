<script>
  import { onDestroy } from "svelte";
  import Icon from "./Icon.svelte";

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
        if (audio.duration && isFinite(audio.duration)) duration = audio.duration;
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
    if (audio.duration && isFinite(audio.duration)) duration = audio.duration;
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
    <button
      class="play-btn"
      onclick={toggle}
      aria-label={isPlaying ? "Pause" : "Play"}
    >
      <Icon name={isPlaying ? "pause" : "play"} size={14} strokeWidth={2.5} />
    </button>
    <span class="timer current">{fmtTime(currentTime)}</span>
    <input
      type="range"
      class="seek-bar"
      min="0"
      max={displayDuration() || 100}
      value={currentTime}
      step="0.1"
      oninput={seek}
      aria-label="Seek"
    >
    <span class="timer total">{fmtTime(displayDuration())}</span>
  </div>
{/if}

<style>
  .player {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 20px;
    background: var(--card);
    border-top: 1px solid var(--border);
  }

  .play-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 999px;
    background: var(--primary);
    color: var(--primary-foreground);
    border: 1px solid transparent;
    box-shadow: var(--shadow-xs);
    transition: background 150ms ease-out;
  }
  .play-btn:hover {
    background: color-mix(in oklch, var(--primary) 90%, black);
  }

  .timer {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    font-variant-numeric: tabular-nums;
    color: var(--muted-foreground);
    min-width: 40px;
  }
  .timer.current { color: var(--foreground); }
  .timer.total { text-align: right; }

  .seek-bar {
    flex: 1;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    background: var(--muted);
    border-radius: 999px;
    cursor: pointer;
  }
  .seek-bar::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 999px;
    background: var(--primary);
    border: 2px solid var(--background);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
  }
  .seek-bar::-moz-range-thumb {
    width: 14px;
    height: 14px;
    border-radius: 999px;
    background: var(--primary);
    border: 2px solid var(--background);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
  }
</style>
