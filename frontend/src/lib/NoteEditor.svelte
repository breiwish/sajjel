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
    // Trailing newline needs a space so backdrop height matches
    if (text.endsWith("\n")) html += "&nbsp;";
    return html;
  }

  function onScroll() {
    if (backdropEl && textareaEl) {
      backdropEl.scrollTop = textareaEl.scrollTop;
    }
  }

  $effect(() => {
    // Reactively update backdrop whenever value changes
    if (backdropEl) {
      backdropEl.innerHTML = highlightedHtml(value);
    }
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
    flex: 1; position: relative; overflow: hidden;
  }
  .backdrop, textarea {
    position: absolute; inset: 0;
    padding: 16px; font-size: 14px; line-height: 1.7;
    font-family: system-ui, sans-serif;
    white-space: pre-wrap; word-wrap: break-word;
    overflow-y: auto; overflow-x: hidden;
    width: 100%; height: 100%;
    border: none; margin: 0;
  }
  .backdrop {
    color: #ddd;
    pointer-events: none;
    z-index: 0;
  }
  .backdrop :global(mark) {
    background: rgba(68, 170, 255, 0.2);
    color: #9dcfff;
    border-radius: 3px;
    padding: 1px 2px;
  }
  textarea {
    color: transparent;
    caret-color: #ddd;
    background: transparent;
    outline: none;
    resize: none;
    z-index: 1;
  }
  textarea::placeholder {
    color: #444;
  }
</style>
