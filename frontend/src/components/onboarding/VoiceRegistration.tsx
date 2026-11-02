import { useCallback, useEffect, useRef, useState } from "react";
import BiometricTips from "./BiometricTips";

type VoiceState = "loading" | "ready" | "recording" | "captured" | "denied";

/* ── WAV encoder (pure JS, no dependencies) ─────────────────────── */

function createWavRecorder(stream: MediaStream) {
	const audioCtx = new AudioContext({ sampleRate: 16000 });
	const source = audioCtx.createMediaStreamSource(stream);
	const processor = audioCtx.createScriptProcessor(4096, 1, 1);

	const pcmChunks: Float32Array[] = [];

	processor.onaudioprocess = (e) => {
		const input = e.inputBuffer.getChannelData(0);
		pcmChunks.push(new Float32Array(input));
	};

	source.connect(processor);
	processor.connect(audioCtx.destination);

	return {
		stop(): Blob {
			processor.disconnect();
			source.disconnect();
			audioCtx.close();

			const totalLength = pcmChunks.reduce((sum, c) => sum + c.length, 0);
			const pcm = new Float32Array(totalLength);
			let offset = 0;
			for (const chunk of pcmChunks) {
				pcm.set(chunk, offset);
				offset += chunk.length;
			}

			return encodeWav(pcm, 16000);
		},
	};
}

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
	const numChannels = 1;
	const bitsPerSample = 16;
	const byteRate = sampleRate * numChannels * (bitsPerSample / 8);
	const blockAlign = numChannels * (bitsPerSample / 8);
	const dataLength = samples.length * (bitsPerSample / 8);
	const buffer = new ArrayBuffer(44 + dataLength);
	const view = new DataView(buffer);

	writeString(view, 0, "RIFF");
	view.setUint32(4, 36 + dataLength, true);
	writeString(view, 8, "WAVE");

	writeString(view, 12, "fmt ");
	view.setUint32(16, 16, true);
	view.setUint16(20, 1, true);
	view.setUint16(22, numChannels, true);
	view.setUint32(24, sampleRate, true);
	view.setUint32(28, byteRate, true);
	view.setUint16(32, blockAlign, true);
	view.setUint16(34, bitsPerSample, true);

	writeString(view, 36, "data");
	view.setUint32(40, dataLength, true);

	let idx = 44;
	for (let i = 0; i < samples.length; i++, idx += 2) {
		const s = Math.max(-1, Math.min(1, samples[i]));
		view.setInt16(idx, s < 0 ? s * 0x8000 : s * 0x7fff, true);
	}

	return new Blob([buffer], { type: "audio/wav" });
}

function writeString(view: DataView, offset: number, str: string) {
	for (let i = 0; i < str.length; i++) {
		view.setUint8(offset + i, str.charCodeAt(i));
	}
}

/* ── Component ──────────────────────────────────────────────────── */

export default function VoiceRegistration({
	onCaptured,
}: {
	onCaptured: (blob: Blob | null) => void;
}) {
	const streamRef = useRef<MediaStream | null>(null);
	const wavRecorderRef = useRef<ReturnType<typeof createWavRecorder> | null>(null);
	const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const [state, setState] = useState<VoiceState>("loading");
	const [error, setError] = useState("");
	const [elapsed, setElapsed] = useState(0);

	/* ── Request microphone ──────────────────────── */
	const initMic = useCallback(async () => {
		setState("loading");
		setError("");
		setElapsed(0);
		onCaptured(null);

		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			streamRef.current = stream;
			setState("ready");
		} catch {
			setState("denied");
			setError("Microphone access is required to record your voice.");
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	useEffect(() => {
		initMic();
		return () => cleanup();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	function cleanup() {
		stopTimer();
		if (wavRecorderRef.current) {
			try { wavRecorderRef.current.stop(); } catch { /* already stopped */ }
			wavRecorderRef.current = null;
		}
		streamRef.current?.getTracks().forEach((t) => t.stop());
		streamRef.current = null;
	}

	/* ── Timer ────────────────────────────────────── */
	function startTimer() {
		setElapsed(0);
		timerRef.current = setInterval(() => setElapsed((s) => s + 1), 1000);
	}
	function stopTimer() {
		if (timerRef.current) {
			clearInterval(timerRef.current);
			timerRef.current = null;
		}
	}

	function formatTime(secs: number) {
		const m = String(Math.floor(secs / 60)).padStart(2, "0");
		const s = String(secs % 60).padStart(2, "0");
		return `${m}:${s}`;
	}

	/* ── Start recording ─────────────────────────── */
	function startRecording() {
		const stream = streamRef.current;
		if (!stream) return;

		setError("");
		wavRecorderRef.current = createWavRecorder(stream);
		setState("recording");
		startTimer();
	}

	/* ── Stop recording ──────────────────────────── */
	function stopRecording() {
		stopTimer();
		if (!wavRecorderRef.current) return;

		const audioBlob = wavRecorderRef.current.stop();
		wavRecorderRef.current = null;

		setState("captured");
		onCaptured(audioBlob);
	}

	/* ── Record again ─────────────────────────────── */
	function recordAgain() {
		cleanup();
		initMic();
	}

	/* ── Render ───────────────────────────────────── */
	const isRecording = state === "recording";

	return (
		<section className="biometric-card" aria-labelledby="voice-registration-title">
			<header className="biometric-card__header">
				<span className="biometric-card__icon material-symbols-outlined" aria-hidden="true">mic</span>
				<div>
					<h2 id="voice-registration-title">Voice Registration</h2>
					<p>Click the microphone and read the sentence in a clear voice.</p>
				</div>
				{state === "captured" && (
					<span className="biometric-badge biometric-badge--ready" aria-label="Voice captured">
						<span className="material-symbols-outlined" aria-hidden="true">check_circle</span>
					</span>
				)}
			</header>

			<div className={`voice-control${isRecording ? " voice-control--recording" : ""}`}>
				<div className="voice-control__rings" aria-hidden="true"><span /><span /><span /></div>

				{state === "loading" && (
					<div className="biometric-loader" aria-label="Requesting microphone">
						<span className="biometric-loader__spinner" />
						<span>Requesting mic…</span>
					</div>
				)}

				{state === "denied" && (
					<div className="biometric-denied">
						<span className="material-symbols-outlined" aria-hidden="true">mic_off</span>
						<span>Mic access denied</span>
					</div>
				)}

				{state !== "loading" && state !== "denied" && (
					<>
						{isRecording ? (
							<button
								className="voice-control__button voice-control__button--stop"
								type="button"
								onClick={stopRecording}
								aria-label="Stop recording"
							>
								<span className="voice-control__stop-icon" aria-hidden="true" />
							</button>
						) : state === "captured" ? (
							<button
								className="voice-control__button voice-control__button--done"
								type="button"
								disabled
								aria-label="Voice captured"
							>
								<span className="material-symbols-outlined">check</span>
							</button>
						) : (
							<button
								className="voice-control__button"
								type="button"
								disabled={state !== "ready"}
								onClick={startRecording}
								aria-label="Start recording"
							>
								<span className="material-symbols-outlined">mic</span>
							</button>
						)}
					</>
				)}

				{isRecording ? (
					<p className="voice-control__status">
						<span className="voice-control__rec-dot" aria-hidden="true" />
						Recording… {formatTime(elapsed)}
					</p>
				) : state === "captured" ? (
					<p className="voice-control__status voice-control__status--done">
						<span className="material-symbols-outlined" aria-hidden="true">check_circle</span>
						Voice captured
					</p>
				) : state !== "loading" && state !== "denied" ? (
					<p>Click to start recording</p>
				) : null}
			</div>

			<div className="voice-sentence">
				<span>Read this sentence</span>
				<strong>"Today is a great day to learn<br /> something new."</strong>
			</div>

			{/* Error */}
			{error && (
				<p className="biometric-error" role="alert">
					<span className="material-symbols-outlined" aria-hidden="true">error</span>
					{error}
				</p>
			)}

			{/* Record again */}
			{state === "captured" && (
				<button className="biometric-action biometric-action--secondary" type="button" onClick={recordAgain}>
					<span className="material-symbols-outlined" aria-hidden="true">refresh</span>
					Record Again
				</button>
			)}

			<BiometricTips
				title="Tips for better audio"
				tips={["Be in a quiet environment", "Speak clearly and naturally", "Keep the microphone close", "Read the sentence once"]}
			/>
		</section>
	);
}