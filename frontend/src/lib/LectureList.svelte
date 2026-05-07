<script>
  import { onMount } from "svelte";
  import Icon from "./Icon.svelte";
  import { listLectures, deleteLecture } from "../api.js";

  let { onselect } = $props();

  let lectures = $state([]);

  export async function refresh() {
    lectures = await listLectures();
  }

  onMount(refresh);

  function fmtDuration(s) {
    if (!s) return "—";
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  function fmtDate(iso) {
    if (!iso) return "";
    return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
  }

  async function remove(id) {
    if (!confirm("Delete this lecture and its audio?")) return;
    await deleteLecture(id);
    await refresh();
  }
</script>

<div class="lecture-list">
  <div class="list-header">
    <div>
      <h1>Lectures</h1>
      <p class="lead">Recorded sessions and their notes.</p>
    </div>
  </div>

  {#if lectures.length === 0}
    <div class="empty-state">
      <span class="empty-icon"><Icon name="file-audio" size={28} /></span>
      <h3>No lectures yet</h3>
      <p>Record one to get started. Your notes will sync to the audio so you can scrub back to any moment.</p>
    </div>
  {:else}
    <div class="grid">
      {#each lectures as lec}
        <article class="card" onclick={() => onselect?.(lec)}>
          <div class="card-body">
            <h2 class="card-title">{lec.title}</h2>
            <div class="card-meta">
              <span>{fmtDate(lec.date)}</span>
              <span class="dot">·</span>
              <span class="mono">{fmtDuration(lec.duration)}</span>
            </div>
          </div>
          <div class="card-foot">
            <span class="badge" class:transcribed={lec.status === "transcribed"}>
              {lec.status}
            </span>
            <button
              class="delete-btn"
              aria-label="Delete lecture"
              onclick={(e) => { e.stopPropagation(); remove(lec.id); }}
            >
              <Icon name="trash" size={14} />
            </button>
          </div>
        </article>
      {/each}
    </div>
  {/if}
</div>

<style>
  .lecture-list {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 32px 80px;
  }

  .list-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 28px;
  }
  h1 {
    font-size: var(--text-3xl);
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--foreground);
    margin: 0 0 4px 0;
  }
  .lead {
    font-size: var(--text-sm);
    color: var(--muted-foreground);
    margin: 0;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 64px 24px;
    border: 1px dashed var(--border);
    border-radius: var(--radius-xl);
    background: var(--card);
    color: var(--muted-foreground);
    max-width: 480px;
    margin: 24px auto;
  }
  .empty-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 999px;
    background: var(--muted);
    color: var(--muted-foreground);
    margin-bottom: 16px;
  }
  .empty-state h3 {
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--foreground);
    margin: 0 0 6px 0;
  }
  .empty-state p {
    font-size: var(--text-sm);
    line-height: 1.55;
    max-width: 320px;
    margin: 0;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 14px;
  }

  .card {
    display: flex;
    flex-direction: column;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-xs);
    cursor: pointer;
    transition: box-shadow 150ms ease-out, border-color 150ms ease-out, transform 150ms ease-out;
    overflow: hidden;
  }
  .card:hover {
    box-shadow: var(--shadow-sm);
    border-color: color-mix(in oklch, var(--border) 60%, var(--ring));
  }
  .card:active { transform: translateY(1px); }

  .card-body {
    padding: 18px 18px 12px;
    flex: 1;
  }
  .card-title {
    font-size: var(--text-base);
    font-weight: 600;
    color: var(--foreground);
    letter-spacing: -0.01em;
    margin: 0 0 6px 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: var(--text-xs);
    color: var(--muted-foreground);
  }
  .mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
  .dot { opacity: 0.5; }

  .card-foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-top: 1px solid var(--border);
    background: color-mix(in oklch, var(--card) 85%, var(--surface));
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
    text-transform: capitalize;
  }
  .badge.transcribed {
    background: color-mix(in oklch, var(--ring) 22%, transparent);
    color: color-mix(in oklch, var(--ring) 70%, var(--foreground));
  }
  .delete-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    color: var(--muted-foreground);
    background: transparent;
    transition: background 100ms ease-out, color 100ms ease-out;
  }
  .delete-btn:hover {
    background: color-mix(in oklch, var(--destructive) 15%, transparent);
    color: var(--destructive);
  }
</style>
