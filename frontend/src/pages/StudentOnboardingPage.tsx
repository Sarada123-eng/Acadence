import { useState, type FormEvent } from "react";
import { registerStudent } from "../api/students";
import "./StudentOnboardingPage.css";

function CampusSketch() {
	return (
		<svg className="student-sketch" viewBox="0 0 520 250" aria-hidden="true">
			<path d="M22 210h474M38 206c24-19 38-42 42-72m-8 72c18-23 34-43 50-58" />
			<path d="M108 202V91l104-42 104 42v111M130 202v-78h164v78M151 124v78m34-78v78m35-78v78m35-78v78" />
			<path d="M92 91h241M112 79 212 34l100 45M160 62h104M174 34v-16h76v16" />
			<path d="M350 204V118l56-25 56 25v86M366 204v-55h80v55M381 149v55m27-55v55" />
			<path d="M40 205c9-17 17-23 27-27m-12 29c13-10 22-12 34-12m346 10c8-16 15-23 25-29m-16 31c13-9 23-11 35-10" />
		</svg>
	);
}

export default function StudentOnboardingPage() {
	const [name, setName] = useState("");
	const [submitted, setSubmitted] = useState(false);
	const [isRegistering, setIsRegistering] = useState(false);
	const [apiError, setApiError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSubmitted(true);
		setApiError("");
		setSuccessMessage("");
		if (isRegistering || !name.trim()) return;

		setIsRegistering(true);
		try {
			const student = await registerStudent({ name: name.trim() });
			sessionStorage.setItem("acadence.studentId", String(student.id));
			sessionStorage.setItem("acadence.studentName", student.name);
			window.location.assign("/auth/student/biometrics");
		} catch (error) {
			setApiError(error instanceof Error ? error.message : "Unable to save your name. Please try again.");
		} finally {
			setIsRegistering(false);
		}
	};

	return (
		<main className="student-onboarding">
			<header className="student-onboarding__header">
				<a className="student-onboarding__wordmark" href="/onboarding" aria-label="Back to role selection">Acadence</a>
				<nav className="student-progress" aria-label="Onboarding progress">
					<span className="student-progress__step student-progress__step--active"><i />Basic Info</span>
					<span className="student-progress__line" aria-hidden="true" />
					<span className="student-progress__step"><i />Biometric Setup</span>
					<span className="student-progress__line" aria-hidden="true" />
					<span className="student-progress__step"><i />Complete</span>
				</nav>
			</header>

			<div className="student-onboarding__layout">
				<section className="student-intro" aria-labelledby="student-intro-title">
					<p className="student-intro__note">A more<br />present classroom,<br />for a brighter you<span /></p>
					<h1 id="student-intro-title">Let’s get<br /><em>started</em></h1>
					<div className="student-intro__underline" aria-hidden="true" />
					<p className="student-intro__copy">Create your student account and take the first step towards a more connected learning experience.</p>

					<div className="campus-collage" aria-label="A quiet campus building surrounded by a hand-drawn architectural sketch">
						<div className="campus-collage__blue" aria-hidden="true" />
						<div className="campus-sketch-paper"><CampusSketch /></div>
						<figure className="campus-polaroid">
							<div className="campus-photo" role="img" aria-label="Trees and a modern university building" />
							<figcaption>the place where<br />ideas take root</figcaption>
							<span className="campus-tape" aria-hidden="true" />
						</figure>
						<p className="campus-note campus-note--learn">Learn<br /><span>Attend</span><br />Belong</p>
						<p className="campus-note campus-note--same">same<br />classes,<br />different<br />connections<span /></p>
					</div>
				</section>

				<section className="student-form-sheet" aria-labelledby="student-form-title">
					<p className="student-form-sheet__eyebrow">STEP 1 OF 3</p>
					<h2 id="student-form-title">What’s your name?</h2>
					<p className="student-form-sheet__intro">Enter your full name to create your student account.<br />You can set up your face and voice next.</p>

					<form onSubmit={handleSubmit} noValidate>
						{apiError && <p className="student-form-message student-form-message--error" role="alert">{apiError}</p>}
						{successMessage && <p className="student-form-message student-form-message--success" role="status">{successMessage}</p>}
						<div className="student-field">
							<label htmlFor="student-full-name">Full Name</label>
							<div className={`student-input-wrap${submitted && !name.trim() ? " student-input-wrap--error" : ""}`}>
								<span className="material-symbols-outlined" aria-hidden="true">person</span>
								<input id="student-full-name" type="text" placeholder="Enter your full name" value={name} onChange={(event) => setName(event.target.value)} autoComplete="name" aria-invalid={submitted && !name.trim()} />
							</div>
							{submitted && !name.trim() && <p className="student-field__error" role="alert">Please enter your full name.</p>}
						</div>
						<button className="student-form-sheet__button" type="submit" disabled={isRegistering}>{isRegistering ? "Saving…" : <>Continue <span aria-hidden="true">→</span></>}</button>
					</form>

					<div className="student-next-step"><span />Next: Set up your face and voice<span /></div>
				</section>
			</div>
		</main>
	);
}