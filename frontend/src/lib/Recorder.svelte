<script>
  import Icon from "./Icon.svelte";

  let { onstarted, onstopped } = $props();

  let isRecording = $state(false);
  let mediaRecorder = $state(null);
  let audioChunks = [];
  let recordStart = $state(null);
  let timerInterval;
  let elapsed = $state("0:00");

  function fmtTime(s) {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${String(sec).padStart(2, "0")}`;
  }

  async function convertToWav(blob) {
    const audioContext = new AudioContext();
    const arrayBuffer = await blob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
    const wavBytes = encodeWav(audioBuffer);
    audioContext.close();
    return new Blob([wavBytes], { type: "audio/wav" });
  }

  function encodeWav(audioBuffer) {
    const numChannels = 1;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1;
    const bitDepth = 16;
    const channelData = audioBuffer.getChannelData(0);
    const dataLength = channelData.length * (bitDepth / 8);
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);
    const writeString = (offset, str) => {
      for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
    };
    writeString(0, "RIFF");
    view.setUint32(4, 36 + dataLength, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true);
    view.setUint16(32, numChannels * (bitDepth / 8), true);
    view.setUint16(34, bitDepth, true);
    writeString(36, "data");
    view.setUint32(40, dataLength, true);
    let offset = 44;
    for (let i = 0; i < channelData.length; i++) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
    return buffer;
  }

  async function toggle() {
    if (!isRecording) await start();
    else stop();
  }

  async function start() {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      alert("Microphone access denied.");
      return;
    }
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });
      const duration = (Date.now() - recordStart) / 1000;
      const wavBlob = await convertToWav(blob);
      onstopped?.({ blob: wavBlob, duration });
    };
    mediaRecorder.start(200);
    recordStart = Date.now();
    isRecording = true;
    onstarted?.({ recordStart });
    timerInterval = setInterval(() => {
      elapsed = fmtTime((Date.now() - recordStart) / 1000);
    }, 500);
  }

  function stop() {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach((t) => t.stop());
    clearInterval(timerInterval);
    isRecording = false;
  }

  export function getElapsedSeconds() {
    if (!recordStart) return 0;
    return (Date.now() - recordStart) / 1000;
  }
</script>

<div class="recorder">
  <button
    class="rec-btn"
    class:recording={isRecording}
    onclick={toggle}
    aria-label={isRecording ? "Stop recording" : "Start recording"}
  >
    {#if isRecording}
      <Icon name="square" size={14} strokeWidth={2.5} />
      <span>Stop</span>
    {:else}
      <span class="rec-dot"></span>
      <span>Record</span>
    {/if}
  </button>
  <div class="meta">
    <Icon name="clock" size={14} />
    <span class="timer">{elapsed}</span>
    {#if isRecording}
      <span class="status">
        <span class="pulse"></span>
        Recording
      </span>
    {/if}
  </div>
</div>

<style>
  .recorder { display: flex; align-items: center; gap: 12px; }

  .rec-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 32px;
    padding: 0 14px;
    border-radius: var(--radius-md);
    background: var(--destructive);
    color: var(--destructive-foreground);
    font-size: var(--text-sm);
    font-weight: 500;
    border: 1px solid transparent;
    box-shadow: var(--shadow-xs);
    transition: background 150ms ease-out;
  }
  .rec-btn:hover {
    background: color-mix(in oklch, var(--destructive) 88%, black);
  }
  .rec-btn.recording {
    background: var(--secondary);
    color: var(--secondary-foreground);
    border-color: var(--border);
  }
  .rec-btn.recording:hover { background: var(--accent); }

  .rec-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: currentColor;
  }

  .meta {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--muted-foreground);
  }
  .timer {
    font-family: var(--font-mono);
    font-size: var(--text-sm);
    font-variant-numeric: tabular-nums;
    min-width: 44px;
  }

  .status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-left: 6px;
    padding: 2px 8px;
    border-radius: 999px;
    background: color-mix(in oklch, var(--destructive) 15%, transparent);
    color: var(--destructive);
    font-size: var(--text-xs);
    font-weight: 500;
  }
  .pulse {
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: currentColor;
    animation: pulse 1.4s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
  }
</style>
