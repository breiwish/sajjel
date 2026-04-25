<script>
  let { tags = [], currentTime = 0, onjump } = $props();

  function fmtTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  function activeIndex() {
    let active = -1;
    for (let j = 0; j < tags.length; j++) {
      if (tags[j].time <= currentTime + 0.3) active = j;
    }
    return active;
  }
</script>

<div class="tag-pane">
  <h2>Tags</h2>
  <div class="tag-list">
    {#each tags as tag, i}
      <div
        class="tag-item"
        class:active={i === activeIndex()}
        onclick={() => onjump?.(tag)}
      >
        <div class="tag-name">#{tag.name}</div>
        <div class="tag-time">{fmtTime(tag.time)}</div>
      </div>
    {/each}
  </div>
</div>

<style>
  .tag-pane { width: 220px; display: flex; flex-direction: column; border-left: 1px solid #1e1e1e; }
  h2 { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #555; padding: 14px 14px 8px; }
  .tag-list { flex: 1; overflow-y: auto; }
  .tag-item {
    padding: 9px 14px; cursor: pointer; border-left: 3px solid transparent;
    transition: background 0.1s;
  }
  .tag-item:hover { background: #1a1a1a; }
  .tag-item.active { border-left-color: #44aaff; background: #111a22; }
  .tag-name { font-size: 13px; color: #9dcfff; font-weight: 500; }
  .tag-time { font-size: 11px; color: #555; font-family: monospace; margin-top: 2px; }
</style>
