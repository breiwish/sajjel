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
  <div class="transcript-header">
    <h3>Transcript</h3>
    {#if status === "transcribed"}
      <span class="badge badge-success">Ready</span>
    {:else if status === "transcribing"}
      <span class="badge">Working</span>
    {/if}
  </div>

  {#if status === "transcribing"}
    <div class="status-msg">
      <span class="spinner"></span>
      Transcribing… this may take a few minutes.
    </div>
  {:else if transcript && transcript.segments && transcript.segments.length > 0}
    <div class="segments">
      {#each transcript.segments as seg}
        <button
          class="segment"
          class:active={isActive(seg)}
          onclick={() => onseek?.({ time: seg.start })}
        >
          <span class="seg-time">{fmtTime(seg.start)}</span>
          {#if seg.speaker}<span class="seg-speaker">{seg.speaker}</span>{/if}
          <span class="seg-text">{seg.text}</span>
        </button>
      {/each}
    </div>
  {:else if transcript && transcript.content}
    <div class="plain-text">{transcript.content}</div>
  {:else}
    <div class="status-msg empty">No transcript yet. Click <strong>Transcribe</strong> to generate one.</div>
  {/if}
</div>

<style>
  .transcript-pane {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow-y: auto;
    border-top: 1px solid var(--border);
    background: var(--card);
  }
  .transcript-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: var(--card);
    z-index: 1;
  }
  h3 {
    font-size: var(--text-sm);
    font-weight: 600;
    margin: 0;
    color: var(--foreground);
    letter-spacing: -0.01em;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--muted);
    color: var(--muted-foreground);
    font-size: var(--text-xs);
    font-weight: 500;
  }
  .badge-success {
    background: color-mix(in oklch, var(--ring) 22%, transparent);
    color: color-mix(in oklch, var(--ring) 70%, var(--foreground));
  }

  .status-msg {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--muted-foreground);
    font-size: var(--text-sm);
    padding: 32px 24px;
    text-align: center;
  }
  .status-msg.empty {
    color: var(--muted-foreground);
  }
  .status-msg :global(strong) { color: var(--foreground); font-weight: 500; }

  .spinner {
    width: 14px; height: 14px;
    border: 2px solid var(--muted);
    border-top-color: var(--primary);
    border-radius: 999px;
    animation: spin 800ms linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .segments {
    display: flex;
    flex-direction: column;
    padding: 12px 16px 24px;
    gap: 2px;
  }
  .segment {
    display: block;
    padding: 8px 12px;
    border-radius: var(--radius-md);
    text-align: left;
    background: transparent;
    border: 1px solid transparent;
    transition: background 100ms ease-out;
    line-height: 1.6;
  }
  .segment:hover { background: var(--accent); }
  .segment.active {
    background: var(--accent);
    border-color: var(--border);
  }
  .seg-time {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--muted-foreground);
    font-variant-numeric: tabular-nums;
    margin-right: 10px;
  }
  .seg-speaker {
    font-size: var(--text-xs);
    color: var(--primary);
    margin-right: 8px;
    font-weight: 600;
  }
  .seg-text {
    font-size: var(--text-sm);
    color: var(--foreground);
  }

  .plain-text {
    color: var(--foreground);
    font-size: var(--text-sm);
    line-height: 1.75;
    white-space: pre-wrap;
    padding: 20px 24px;
  }
</style>
