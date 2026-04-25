<script>
  import { onMount } from "svelte";
  import { listLectures, deleteLecture } from "../api.js";

  let { onselect } = $props();

  let lectures = $state([]);

  export async function refresh() {
    lectures = await listLectures();
  }

  onMount(refresh);

  function fmtDuration(s) {
    if (!s) return "--";
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
  <h2>Lectures</h2>
  {#if lectures.length === 0}
    <p class="empty">No lectures yet. Record one to get started.</p>
  {/if}
  {#each lectures as lec}
    <div class="lecture-item" onclick={() => onselect?.(lec)}>
      <div class="lecture-title">{lec.title}</div>
      <div class="lecture-meta">
        <span>{fmtDate(lec.date)}</span>
        <span>{fmtDuration(lec.duration)}</span>
        <span class="badge" class:transcribed={lec.status === "transcribed"}>{lec.status}</span>
      </div>
      <button class="delete-btn" onclick={(e) => { e.stopPropagation(); remove(lec.id); }}>✕</button>
    </div>
  {/each}
</div>

<style>
  .lecture-list { padding: 14px; }
  h2 { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: #555; margin-bottom: 10px; }
  .empty { color: #444; font-size: 13px; }
  .lecture-item {
    padding: 10px 12px; border-radius: 6px; cursor: pointer; position: relative;
    border: 1px solid #222; margin-bottom: 6px; transition: background 0.1s;
  }
  .lecture-item:hover { background: #1a1a1a; }
  .lecture-title { font-size: 14px; color: #ddd; font-weight: 500; }
  .lecture-meta { font-size: 11px; color: #555; margin-top: 4px; display: flex; gap: 10px; }
  .badge { padding: 1px 6px; border-radius: 3px; background: #222; }
  .badge.transcribed { background: #1a2a1a; color: #6c6; }
  .delete-btn {
    position: absolute; top: 8px; right: 8px; background: none; border: none;
    color: #444; cursor: pointer; font-size: 14px; padding: 2px 6px;
  }
  .delete-btn:hover { color: #ff4444; }
</style>
