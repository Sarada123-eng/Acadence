export default function OnboardingProgress() {
	return (
		<nav className="biometric-progress" aria-label="Onboarding progress">
			<div className="biometric-progress__step biometric-progress__step--complete">
				<span className="biometric-progress__dot"><span className="material-symbols-outlined">check</span></span>
				<span>Basic Info</span>
			</div>
			<span className="biometric-progress__line biometric-progress__line--complete" aria-hidden="true" />
			<div className="biometric-progress__step biometric-progress__step--current">
				<span className="biometric-progress__dot">2</span>
				<span>Biometric Setup</span>
			</div>
			<span className="biometric-progress__line" aria-hidden="true" />
			<div className="biometric-progress__step">
				<span className="biometric-progress__dot">3</span>
				<span>Complete</span>
			</div>
		</nav>
	);
}