import { useState, type FormEvent } from "react";
import { loginTeacher } from "../api/auth";
import HandwrittenNote from "../components/onboarding/HandwrittenNote";
import "./TeacherLoginPage.css";

export default function TeacherLoginPage() {
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [showPassword, setShowPassword] = useState(false);
	const [submitted, setSubmitted] = useState(false);
	const [isLoggingIn, setIsLoggingIn] = useState(false);
	const [apiError, setApiError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");

	const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
		event.preventDefault();
		setSubmitted(true);
		setApiError("");
		setSuccessMessage("");
		if (isLoggingIn || !username.trim() || !password) return;

		setIsLoggingIn(true);
		try {
			const teacher = await loginTeacher({ username: username.trim(), password });
			const message = `Login successful. Welcome back, ${teacher.name}.`;
			setSuccessMessage(message);
			window.alert(message);
		} catch (error) {
			setApiError(error instanceof Error ? error.message : "Login failed. Please try again.");
		} finally {
			setIsLoggingIn(false);
		}
	};

	return (
		<main className="teacher-login-page">
			<header className="teacher-login-header">
				<a className="teacher-login-logo" href="/" aria-label="Acadence home">
					<img src="/images/acadence-logo.png" alt="Acadence" />
					<span>PEOPLE · LEARNING · INTEGRITY</span>
				</a>
				<a className="teacher-login-home" href="/">← Back to Home</a>
			</header>

			<div className="teacher-login-leaves teacher-login-leaves--top" aria-hidden="true">
				<span /><span /><span /><span /><span />
			</div>
			<div className="teacher-login-leaves teacher-login-leaves--bottom" aria-hidden="true">
				<span /><span /><span /><span />
			</div>
			<div className="teacher-login-books" aria-hidden="true">
				<span>TEACH</span><span>INSPIRE</span><span>BELONG</span><span>MAKE A DIFFERENCE</span>
			</div>
			<HandwrittenNote className="teacher-login-note teacher-login-note--left">Same<br />Classrooms.<br />Brighter<br />Tomorrow.<span className="note-underline" /></HandwrittenNote>
			<HandwrittenNote className="teacher-login-note teacher-login-note--right">Good<br />Teachers<br />Build<br />Brighter<br />Futures.<span className="note-underline" /></HandwrittenNote>
			<HandwrittenNote className="teacher-login-note teacher-login-note--bottom">A more human<br />way to learn<span className="note-underline" /></HandwrittenNote>

			<section className="teacher-login-content" aria-labelledby="teacher-login-title">
				<p className="teacher-login-eyebrow">EDUCATE · GUIDE · EMPOWER</p>
				<h1 id="teacher-login-title">Teacher Login</h1>
				<p className="teacher-login-intro">Welcome back, teacher.<br />Continue where your classroom left off.</p>

				<div className="teacher-login-card">
					<form onSubmit={handleSubmit} noValidate>
						{apiError && <p className="teacher-login-form-message teacher-login-form-message--error" role="alert">{apiError}</p>}
						{successMessage && <p className="teacher-login-form-message teacher-login-form-message--success" role="status">{successMessage}</p>}
						<div className="teacher-login-field">
							<label htmlFor="teacher-login-username">Username</label>
							<div className="teacher-login-input-wrap">
								<span className="teacher-login-input-icon" aria-hidden="true"><span className="material-symbols-outlined">
person
</span></span>
								<input id="teacher-login-username" type="text" placeholder="Enter your username" value={username} onChange={(event) => setUsername(event.target.value)} aria-invalid={submitted && !username.trim()} />
							</div>
							{submitted && !username.trim() && <p className="teacher-login-error" role="alert">Username is required.</p>}
						</div>

						<div className="teacher-login-field">
							<label htmlFor="teacher-login-password">Password</label>
							<div className="teacher-login-input-wrap">
								<span className="teacher-login-input-icon" aria-hidden="true"><span className="material-symbols-outlined">
lock
</span></span>
								<input id="teacher-login-password" type={showPassword ? "text" : "password"} placeholder="Enter your password" value={password} onChange={(event) => setPassword(event.target.value)} aria-invalid={submitted && !password} />
								<button className="teacher-login-eye" type="button" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <span className="material-symbols-outlined">
undereye
</span> : <span className="material-symbols-outlined">
looks
</span>}</button>
							</div>
							{submitted && !password && <p className="teacher-login-error" role="alert">Password is required.</p>}
						</div>

						<button className="teacher-login-submit" type="submit" disabled={isLoggingIn}>{isLoggingIn ? "Logging in…" : <>Log in <span aria-hidden="true">→</span></>}</button>
					</form>

					<div className="teacher-login-register">
						<div className="teacher-login-divider"><span>NEW HERE?</span></div>
						<p>Don't have an account? <a href="/auth/teacher">Register now →</a></p>
					</div>
				</div>
			</section>

			<div className="teacher-login-footer">✦ &nbsp; PEOPLE · LEARNING · INTEGRITY <span /></div>
		</main>
	);
}