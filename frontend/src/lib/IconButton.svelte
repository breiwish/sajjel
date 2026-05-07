<script>
  let { label, onclick, children } = $props();
</script>

<button class="icon-btn" aria-label={label} {onclick}>
  {@render children?.()}
</button>

<style>
  .icon-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: var(--radius-md);
    color: var(--muted-foreground);
    background: transparent;
    border: 1px solid transparent;
    transition: background 150ms ease-out, color 150ms ease-out, border-color 150ms ease-out;
  }
  .icon-btn:hover {
    background: var(--accent);
    color: var(--accent-foreground);
  }
</style>
