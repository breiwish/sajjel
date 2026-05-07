<script>
  // Lucide icon — inline SVG. 24x24 viewBox, 2px stroke, currentColor.
  // We hand-roll a minimal subset to avoid a dependency.
  let { name, size = 16, strokeWidth = 2 } = $props();

  const PATHS = {
    plus:        ['<path d="M5 12h14"/>', '<path d="M12 5v14"/>'],
    "arrow-left": ['<path d="m12 19-7-7 7-7"/>', '<path d="M19 12H5"/>'],
    save:        ['<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>', '<polyline points="17 21 17 13 7 13 7 21"/>', '<polyline points="7 3 7 8 15 8"/>'],
    sparkles:    ['<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>', '<path d="M20 3v4"/>', '<path d="M22 5h-4"/>', '<path d="M4 17v2"/>', '<path d="M5 18H3"/>'],
    moon:        ['<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>'],
    sun:         ['<circle cx="12" cy="12" r="4"/>', '<path d="M12 2v2"/>', '<path d="M12 20v2"/>', '<path d="m4.93 4.93 1.41 1.41"/>', '<path d="m17.66 17.66 1.41 1.41"/>', '<path d="M2 12h2"/>', '<path d="M20 12h2"/>', '<path d="m6.34 17.66-1.41 1.41"/>', '<path d="m19.07 4.93-1.41 1.41"/>'],
    play:        ['<polygon points="6 3 20 12 6 21 6 3"/>'],
    pause:       ['<rect x="14" y="4" width="4" height="16" rx="1"/>', '<rect x="6" y="4" width="4" height="16" rx="1"/>'],
    mic:         ['<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>', '<path d="M19 10v2a7 7 0 0 1-14 0v-2"/>', '<line x1="12" x2="12" y1="19" y2="22"/>'],
    square:      ['<rect width="14" height="14" x="5" y="5" rx="1.5"/>'],
    x:           ['<path d="M18 6 6 18"/>', '<path d="m6 6 12 12"/>'],
    trash:       ['<path d="M3 6h18"/>', '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>', '<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'],
    tag:         ['<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/>', '<circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>'],
    clock:       ['<circle cx="12" cy="12" r="10"/>', '<polyline points="12 6 12 12 16 14"/>'],
    "file-audio":['<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>', '<polyline points="14 2 14 8 20 8"/>', '<path d="M10 20a3 3 0 0 1-3-3v-4a3 3 0 0 1 6 0v4a3 3 0 0 1-3 3z"/>'],
  };

  let inner = $derived((PATHS[name] || []).join(""));
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={strokeWidth}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>{@html inner}</svg>

<style>
  svg { display: inline-block; flex-shrink: 0; vertical-align: middle; }
</style>
