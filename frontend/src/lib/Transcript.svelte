<script>
  let { transcript = null, status = "recorded", currentTime = 0, onseek } = $props();

  function fmtTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  function isActive(seg) {
    return currentTime >= seg.start && currentTime < seg.end;
  }
</script>

<div class="transcript-pane">
  {#if status === "transcribing"}
    <div class="status-msg">Transcribing… this may take a few minutes.</div>
  {:else if transcript && transcript.segments && transcript.segments.length > 0}
    <div class="segments">
      {#each transcript.segments as seg}
        <div
          class="segment"
          class:active={isActive(seg)}
          onclick={() => onseek?.({ time: seg.start })}
        >
          <span class="seg-time">{fmtTime(seg.start)}</span>
          {#if seg.speaker}<span class="seg-speaker">{seg.speaker}</span>{/if}
          <span class="seg-text">{seg.text}</span>
        </div>
      {/each}
    </div>
  {:else if transcript && transcript.content}
    <div class="plain-text">{transcript.content}</div>
  {:else}
    <div class="status-msg empty">No transcript yet. Click "Transcribe" after recording.</div>
  {/if}
</div>

<style>
  .transcript-pane { padding: 16px; overflow-y: auto; flex: 1; }
  .status-msg { color: #666; font-size: 13px; padding: 20px; text-align: center; }
  .status-msg.empty { color: #444; }
  .segments { display: flex; flex-direction: column; gap: 2px; }
  .segment {
    padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;
    line-height: 1.6; transition: background 0.1s;
  }
  .segment:hover { background: #1a1a1a; }
  .segment.active { background: #111a22; }
  .seg-time { font-size: 11px; font-family: monospace; color: #555; margin-right: 8px; }
  .seg-speaker { font-size: 11px; color: #9dcfff; margin-right: 6px; font-weight: 600; }
  .seg-text { color: #ddd; }
  .plain-text { color: #ddd; font-size: 14px; line-height: 1.7; white-space: pre-wrap; }
</style>
