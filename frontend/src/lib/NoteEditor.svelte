<script>
  let { value = $bindable(""), getTimestamp = () => 0, disabled = false, onnewtag, onchange } = $props();

  let knownTags = new Set();
  let textareaEl = $state(null);
  let backdropEl = $state(null);

  const TAG_OFFSET = 2;

  function onInput() {
    detectTags();
    onchange?.({ value });
  }

  function detectTags() {
    const re = /#([^#\n]+)#/g;
    let match;
    while ((match = re.exec(value)) !== null) {
      const charIndex = match.index;
      if (!knownTags.has(charIndex)) {
        knownTags.add(charIndex);
        const rawTime = getTimestamp();
        onnewtag?.({ name: match[1].trim(), time: Math.max(0, rawTime - TAG_OFFSET), charIndex });
      }
    }
  }

  function highlightedHtml(text) {
    let html = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/#([^#\n]+)#/g, '<mark>$&</mark>')
      .replace(/\n/g, "<br>");
    if (text.endsWith("\n")) html += "&nbsp;";
    return html;
  }

  function onScroll() {
    if (backdropEl && textareaEl) backdropEl.scrollTop = textareaEl.scrollTop;
  }

  $effect(() => {
    if (backdropEl) backdropEl.innerHTML = highlightedHtml(value);
  });
</script>

<div class="editor-wrap">
  <div class="backdrop" bind:this={backdropEl}></div>
  <textarea
    bind:this={textareaEl}
    bind:value
    oninput={onInput}
    onscroll={onScroll}
    {disabled}
    placeholder="Start recording, then type notes… Use #Tag Name# to mark moments"
    spellcheck="false"
  ></textarea>
</div>

<style>
  .editor-wrap {
    flex: 1;
    position: relative;
    overflow: hidden;
    background: var(--background);
  }
  .backdrop, textarea {
    position: absolute;
    inset: 0;
    padding: 28px 32px;
    font-size: var(--text-base);
    line-height: 1.75;
    font-family: var(--font-sans);
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-y: auto;
    overflow-x: hidden;
    width: 100%;
    height: 100%;
    border: none;
    margin: 0;
  }
  .backdrop {
    color: var(--foreground);
    pointer-events: none;
    z-index: 0;
  }
  .backdrop :global(mark) {
    background: color-mix(in oklch, var(--ring) 22%, transparent);
    color: var(--foreground);
    border-radius: var(--radius-sm);
    padding: 1px 4px;
    font-weight: 500;
    box-shadow: inset 0 -1px 0 color-mix(in oklch, var(--ring) 50%, transparent);
  }
  textarea {
    color: transparent;
    caret-color: var(--foreground);
    background: transparent;
    outline: none;
    resize: none;
    z-index: 1;
  }
  textarea::placeholder { color: var(--muted-foreground); opacity: 0.6; }
  textarea:disabled { cursor: default; }
</style>
