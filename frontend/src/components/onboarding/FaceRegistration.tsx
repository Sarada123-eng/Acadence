import { useCallback, useEffect, useRef, useState } from "react";
import BiometricTips from "./BiometricTips";

type FaceState = "loading" | "ready" | "capturing" | "captured" | "denied";

export default function FaceRegistration({
	onCaptured,
}: {
	onCaptured: (blob: Blob | null) => void;
}) {
	const videoRef = useRef<HTMLVideoElement>(null);
	const canvasRef = useRef<HTMLCanvasElement>(null);
	const streamRef = useRef<MediaStream | null>(null);

	const [state, setState] = useState<FaceState>("loading");
	const [capturedUrl, setCapturedUrl] = useState<string | null>(null);
	const [error, setError] = useState("");

	/* ── Start camera ─────────────────────────────── */
	const startCamera = useCallback(async () => {
		setState("loading");
		setError("");
		setCapturedUrl(null);
		onCaptured(null);

		try {
			const stream = await navigator.mediaDevices.getUserMedia({ video: true });
			streamRef.current = stream;
			if (videoRef.current) {
				videoRef.current.srcObject = stream;
			}
			setState("ready");
		} catch {
			setState("denied");
			setError("Camera access is required to capture your face.");
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	useEffect(() => {
		startCamera();
		return () => stopCamera();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	function stopCamera() {
		streamRef.current?.getTracks().forEach((t) => t.stop());
		streamRef.current = null;
	}

	/* ── Capture a single frame ───────────────────── */
	async function capturePhoto() {
		const video = videoRef.current;
		const canvas = canvasRef.current;
		if (!video || !canvas) return;

		setState("capturing");

		canvas.width = video.videoWidth;
		canvas.height = video.videoHeight;
		const ctx = canvas.getContext("2d");
		if (!ctx) {
			setError("Unable to capture the photo. Please try again.");
			setState("ready");
			return;
		}

		ctx.drawImage(video, 0, 0);

		const blob = await new Promise<Blob | null>((resolve) =>
			canvas.toBlob(resolve, "image/jpeg", 0.9),
		);

		if (!blob) {
			setError("Unable to capture the photo. Please try again.");
			setState("ready");
			return;
		}

		/* Show captured still, pause video */
		const url = URL.createObjectURL(blob);
		setCapturedUrl(url);
		stopCamera();
		setState("captured");
		onCaptured(blob);
	}

	/* ── Retake ───────────────────────────────────── */
	function retake() {
		if (capturedUrl) URL.revokeObjectURL(capturedUrl);
		setCapturedUrl(null);
		onCaptured(null);
		startCamera();
	}

	/* ── Render ───────────────────────────────────── */
	const showVideo = !capturedUrl && state !== "denied";
	const showCaptured = !!capturedUrl;

	return (
		<section className="biometric-card" aria-labelledby="face-registration-title">
			<header className="biometric-card__header">
				<span className="biometric-card__icon material-symbols-outlined" aria-hidden="true">photo_camera</span>
				<div>
					<h2 id="face-registration-title">Face Registration</h2>
					<p>Look at the camera and click capture.</p>
				</div>
				{state === "captured" && (
					<span className="biometric-badge biometric-badge--ready" aria-label="Photo captured">
						<span className="material-symbols-outlined" aria-hidden="true">check_circle</span>
					</span>
				)}
			</header>

			{/* Hidden canvas for frame capture */}
			<canvas ref={canvasRef} style={{ display: "none" }} />

			<div className="face-preview" aria-label="Camera preview">
				<span className="face-preview__corner face-preview__corner--tl" />
				<span className="face-preview__corner face-preview__corner--tr" />
				<span className="face-preview__corner face-preview__corner--bl" />
				<span className="face-preview__corner face-preview__corner--br" />

				{state === "loading" && (
					<div className="biometric-loader" aria-label="Starting camera">
						<span className="biometric-loader__spinner" />
						<span>Starting camera…</span>
					</div>
				)}

				{state === "denied" && (
					<div className="biometric-denied">
						<span className="material-symbols-outlined" aria-hidden="true">videocam_off</span>
						<span>Camera access denied</span>
					</div>
				)}

				{showVideo && (
					<video
						ref={videoRef}
						className="face-preview__video"
						autoPlay
						playsInline
						muted
					/>
				)}

				{showCaptured && (
					<img src={capturedUrl} alt="Captured face" className="face-preview__captured" />
				)}

				{!showVideo && !showCaptured && state !== "loading" && state !== "denied" && (
					<span className="face-preview__person material-symbols-outlined" aria-hidden="true">face</span>
				)}
			</div>

			{/* Error message */}
			{error && (
				<p className="biometric-error" role="alert">
					<span className="material-symbols-outlined" aria-hidden="true">error</span>
					{error}
				</p>
			)}

			{/* Action buttons */}
			{state === "captured" ? (
				<button className="biometric-action biometric-action--secondary" type="button" onClick={retake}>
					<span className="material-symbols-outlined" aria-hidden="true">refresh</span>
					Retake Photo
				</button>
			) : (
				<button
					className="biometric-action"
					type="button"
					disabled={state !== "ready"}
					onClick={capturePhoto}
				>
					<span className="material-symbols-outlined" aria-hidden="true">photo_camera</span>
					Capture Photo
				</button>
			)}

			<BiometricTips
				title="Tips for a good photo"
				tips={["Ensure good lighting", "Keep your face clearly visible", "Look directly at the camera", "Remove glasses if possible"]}
			/>
		</section>
	);
}