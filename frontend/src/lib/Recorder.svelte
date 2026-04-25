<script>
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
      for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
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
  <button class="rec-btn" class:recording={isRecording} onclick={toggle}>
    {isRecording ? "⏹ Stop" : "⏺ Record"}
  </button>
  <span class="timer">{elapsed}</span>
  {#if isRecording}
    <span class="status recording">recording</span>
  {/if}
</div>

<style>
  .recorder { display: flex; align-items: center; gap: 10px; }
  .rec-btn {
    border: none; cursor: pointer; border-radius: 6px; font-size: 13px;
    padding: 7px 14px; background: #ff4444; color: #fff; transition: background 0.15s;
  }
  .rec-btn:hover { background: #ff2222; }
  .rec-btn.recording { background: #555; }
  .rec-btn.recording:hover { background: #444; }
  .timer { font-size: 13px; font-family: monospace; color: #888; min-width: 48px; }
  .status { font-size: 12px; }
  .status.recording { color: #ff4444; }
</style>
