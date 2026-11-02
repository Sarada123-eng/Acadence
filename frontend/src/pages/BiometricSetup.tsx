import { useState } from "react";
import FaceRegistration from "../components/onboarding/FaceRegistration";
import OnboardingProgress from "../components/onboarding/OnboardingProgress";
import VoiceRegistration from "../components/onboarding/VoiceRegistration";
import { uploadFace, uploadVoice } from "../services/biometricApi";
import "./BiometricSetup.css";

export default function BiometricSetup() {
	const studentId = sessionStorage.getItem("acadence.studentId") ?? "";
	const studentName = sessionStorage.getItem("acadence.studentName") || "Student";

	const [faceBlob, setFaceBlob] = useState<Blob | null>(null);
	const [voiceBlob, setVoiceBlob] = useState<Blob | null>(null);
	const [enrolling, setEnrolling] = useState(false);
	const [enrolled, setEnrolled] = useState(false);
	const [enrollError, setEnrollError] = useState("");

	async function handleEnroll() {
		if (!faceBlob || !voiceBlob || !studentId) return;

		setEnrolling(true);
		setEnrollError("");

		try {
			await uploadFace(studentId, faceBlob);
			await uploadVoice(studentId, voiceBlob);
			setEnrolled(true);
		} catch (err: unknown) {
			const message = err instanceof Error ? err.message : "Failed to enroll biometrics. Please try again.";
			setEnrollError(message);
		} finally {
			setEnrolling(false);
		}
	}

	function handleComplete() {
		if (!enrolled) return;
		// Navigate to next onboarding step or main dashboard
		window.location.assign("/onboarding");
	}

	/* If no student ID, redirect back */
	if (!studentId) {
		return (
			<main className="biometric-setup">
				<div className="biometric-setup__missing">
					<span className="material-symbols-outlined" aria-hidden="true">error</span>
					<p>Student session not found. Please register first.</p>
					<a className="biometric-action" href="/auth/student">Go to Registration</a>
				</div>
			</main>
		);
	}

	return (
		<main className="biometric-setup">
			<header className="biometric-setup__header">
				<a className="biometric-setup__wordmark" href="/" aria-label="Acadence home">Acadence</a>
				<div className="biometric-setup__profile" aria-label={`Signed in as ${studentName}`}>
					<span className="biometric-setup__avatar">{studentName.charAt(0).toUpperCase()}</span>
					<span><strong>{studentName}</strong><small>Student</small></span>
					<span className="material-symbols-outlined" aria-hidden="true">expand_more</span>
				</div>
			</header>

			<OnboardingProgress />

			<section className="biometric-setup__intro" aria-labelledby="biometric-title">
				<h1 id="biometric-title">Register your biometrics</h1>
				<p>Capture your face and record a short voice sample. This helps Acadence<br className="biometric-setup__desktop-break" /> recognize you in your classrooms.</p>
			</section>

			<div className="biometric-cards">
				<FaceRegistration
					onCaptured={(blob) => {
						setFaceBlob(blob);
						setEnrolled(false);
						setEnrollError("");
					}}
				/>
				<VoiceRegistration
					onCaptured={(blob) => {
						setVoiceBlob(blob);
						setEnrolled(false);
						setEnrollError("");
					}}
				/>
			</div>

			<div className="biometric-enroll-container">
				{enrollError && (
					<p className="biometric-error" role="alert">
						<span className="material-symbols-outlined" aria-hidden="true">error</span>
						{enrollError}
					</p>
				)}

				{enrolled ? (
					<div className="biometric-success-row">
						<span className="material-symbols-outlined" aria-hidden="true">check_circle</span>
						<span>Biometrics enrolled successfully! Click "Complete Setup" to continue.</span>
					</div>
				) : (
					<button
						className="biometric-action biometric-action--enroll"
						type="button"
						disabled={!faceBlob || !voiceBlob || enrolling}
						onClick={handleEnroll}
					>
						{enrolling ? (
							<>
								<span className="biometric-loader__spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
								Enrolling Biometrics…
							</>
						) : (
							<>
								<span className="material-symbols-outlined" aria-hidden="true">fingerprint</span>
								Enroll Biometrics
							</>
						)}
					</button>
				)}
			</div>

			<footer className="biometric-setup__footer">
				<a className="biometric-back" href="/auth/student"><span className="material-symbols-outlined" aria-hidden="true">arrow_back</span> Back</a>
				<button
					className="biometric-complete"
					type="button"
					disabled={!enrolled}
					onClick={handleComplete}
				>
					Complete Setup <span aria-hidden="true">→</span>
				</button>
			</footer>
		</main>
	);
}