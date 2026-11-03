import { useState, type FormEvent } from "react";
import "./StudentJoinPage.css";

export default function StudentJoinPage() {
	const initialCode = new URLSearchParams(window.location.search).get("code") ?? "";
	const [joinCode, setJoinCode] = useState(initialCode);
	const [error, setError] = useState("");

	function handleSubmit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		const code = joinCode.trim();
		if (!code) {
			setError("Enter the classroom code.");
			return;
		}
		sessionStorage.setItem("acadence.pendingJoinCode", code);
		window.location.assign("/auth/student");
	}

	return (
		<main className="classroom-entry">
			<section className="classroom-entry__card">
				<a href="/" className="classroom-entry__logo">Acadence</a>
				<p className="classroom-entry__eyebrow">STUDENT CLASSROOM ENTRY</p>
				<h1>Join your classroom</h1>
				<p>Enter the code shared by your teacher. New students will be guided through registration before joining.</p>
				<form onSubmit={handleSubmit} noValidate>
					<label htmlFor="classroom-code">Classroom code</label>
					<input id="classroom-code" value={joinCode} onChange={(event) => { setJoinCode(event.target.value); setError(""); }} placeholder="e.g. abc123" autoComplete="off" />
					{error && <p className="classroom-entry__error" role="alert">{error}</p>}
					<button type="submit">Continue <span aria-hidden="true">→</span></button>
				</form>
			</section>
		</main>
	);
}
