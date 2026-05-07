<script>
  import Icon from "./Icon.svelte";

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

<aside class="tag-pane">
  <div class="tag-header">
    <Icon name="tag" size={14} />
    <h2>Tags</h2>
    <span class="count">{tags.length}</span>
  </div>
  <div class="tag-list">
    {#if tags.length === 0}
      <p class="empty">Wrap a phrase in <code>#hashes#</code> while recording to mark a moment.</p>
    {/if}
    {#each tags as tag, i}
      <button
        class="tag-item"
        class:active={i === activeIndex()}
        onclick={() => onjump?.(tag)}
      >
        <span class="tag-name">{tag.name}</span>
        <span class="tag-time">{fmtTime(tag.time)}</span>
      </button>
    {/each}
  </div>
</aside>

<style>
  .tag-pane {
    width: 260px;
    display: flex;
    flex-direction: column;
    border-left: 1px solid var(--border);
    background: var(--sidebar);
  }
  .tag-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 16px 16px 12px;
    color: var(--muted-foreground);
  }
  h2 {
    font-size: var(--text-xs);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 600;
    color: var(--muted-foreground);
    flex: 1;
    margin: 0;
  }
  .count {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--muted-foreground);
    background: var(--muted);
    padding: 1px 6px;
    border-radius: var(--radius-sm);
  }
  .tag-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 8px 12px;
  }
  .empty {
    padding: 8px;
    color: var(--muted-foreground);
    font-size: var(--text-xs);
    line-height: 1.5;
  }
  .empty :global(code) {
    background: var(--muted);
    padding: 0 4px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.9em;
  }
  .tag-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    padding: 8px 10px;
    border-radius: var(--radius-md);
    background: transparent;
    border: 1px solid transparent;
    text-align: left;
    transition: background 100ms ease-out, border-color 100ms ease-out;
    margin-bottom: 2px;
  }
  .tag-item:hover {
    background: var(--sidebar-accent);
  }
  .tag-item.active {
    background: var(--sidebar-accent);
    border-color: var(--sidebar-border);
  }
  .tag-name {
    font-size: var(--text-sm);
    font-weight: 500;
    color: var(--sidebar-foreground);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .tag-time {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    color: var(--muted-foreground);
    font-variant-numeric: tabular-nums;
    margin-left: 8px;
    flex-shrink: 0;
  }
  .tag-item.active .tag-time { color: var(--sidebar-primary); }
</style>
